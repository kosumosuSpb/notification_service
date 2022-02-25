from celery import shared_task
from .models import Mailing, Client, Message
from django.db.models import Q
from datetime import datetime, timedelta
import json
import requests
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import mail_admins


def send_mails(mailing):
    """
    Отправка рассылки

    Принимает объект рассылки, из него - теги и операторов
    по ним фильтрует клиентов и запускает рассылку по ним.

    Если всё отправилось и вернуло ответ True,
    то рассылка помечается, как finished = True

    :param mailing: объект рассылки
    :return: None
    """
    # DEBUG
    print(f'=== send_mails STARTS, id: => {mailing.id} <===')

    # проверяем, запускалась ли уже рассылка:
    # если сообщения уже есть, то запускалась,
    # надо попробовать переслать те, что не получилось
    if mailing.messages.exists():
        # DEBUG
        print('--- найдены недоставленные сообщения, попытка доставить... ---')

        finished = all([send_client(message.client, mailing)
                        for message in mailing.messages.all()
                        if message.sent is False])

    # если сообщений нет, то рассылка ещё не запускалась,
    # формируем её
    else:
        # DEBUG
        print('--- создаём новую рассылку ---')
        print('--- применяем фильтры... ---')

        # достаём фильтры для рассылки
        tags = mailing.tags.all()
        operators = mailing.operators.all()

        # используем Q-объекты, чтобы искать сразу по двум параметрам с помощью оператора | (OR)
        # получаем кверисет клиентов для рассылки
        clients = Client.objects.filter(Q(tag__in=tags) | Q(operator__in=operators))

        # DEBUG
        print('===> START send_mails <===')
        print(clients, mailing.text)

        # перебор клиентов, запуск рассылки по ним и возврат ответов:
        # если все True, то рассылка завершена и её можно закрывать
        finished = all([send_client(client, mailing) for client in clients])

    # DEBUG
    print('===> END send_mails <===')

    # если всё отправилось, то отмечаем рассылку, как завершённый
    mailing.finished = True if finished else False
    mailing.finished_datetime = datetime.now(tz=timezone.utc)
    mailing.save()

    # DEBUG
    print('===> SAVING mailing... <===')
    print(f'===> mailing.finished_datetime: {mailing.finished_datetime} <===')

    # DEBUG
    print(f'===> Finished: {finished} <===')


# функция рассылки сообщения конкретному клиенту
def send_client(client, mailing):
    """
    функция отправки сообщения одному клиенту
    через внешний АПИ сервис c JWT-авторизацией

    адрес:
    https://probe.fbrq.cloud/v1/send/{msgId}

    формат:
    {
      "id": 0,
      "phone": 0,
      "text": "string"
    }

    :param client: объект клиента
    :param mailing: объект рассылки
    :return: True, если успех, False, - если нет
    """
    # в проде должен быть в отдельном файле в гитигноре
    TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzYxNDQ2NzMsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6ImtvbnN0YW50aW4uY2hlcm5vdiJ9.yx543hnuCBuib8ZlWmtmYq7EanWLAHwdkp7zYtd9dq8'

    # создаём экземпляр сообщения для отчётов
    # если он уже существует, то просто извлекаем из БД
    message, created = Message.objects.get_or_create(mailing=mailing, client=client)

    if created:
        message.save()

        # DEBUG
        print(f'--- Сообщение {message.id} создано --- ')
    else:
        # DEBUG
        print(f'--- Сообщение {message.id} извлечено --- ')

    # подготовка и отправка рассылки клиенту
    # адрес внешнего сервиса отправки
    url = 'https://probe.fbrq.cloud/v1/send/'

    # заголовки и авторизация
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'content-type': 'application/json'
    }

    # данные для отправки
    data = json.dumps(
        {
            'id': message.id,
            'phone': int(client.phone_number),
            'text': mailing.text
        }
    )

    # DEBUG
    print('---> START send_client <---')
    print(client, mailing, headers, data)

    try:
        # отправляем данные, ждём ответа 5 секунд
        response = requests.post(url=url + str(message.id), data=data, headers=headers, timeout=5)

        # DEBUG
        print(response)

        response.raise_for_status()

    # исключения можно конкретизировать, если нужно
    except Exception as e:
        print(f'Ошибка: {e}')
        return False
    else:
        if response.status_code == requests.codes.ok:
            # Отмечаем, что отправка прошла успешно
            message.sent_datetime = datetime.now(tz=timezone.utc)
            message.sent = True
            message.save()

            # DEBUG
            print(f'--- Message {message.id} sended: {message.__dict__} --- ')

            return True


# таск для перебора рассылок и отправки не отправленных
@shared_task()
def check_and_send():
    """
    Перебирает рассылки и рассылает те, которые уже нужно и которые не просрочены
    помечает те, которые просрочены
    """
    # DEBUG
    print('=== START check_and_send TASK ===')

    # собираем не отправленные рассылки, которые уже пора отправлять
    mailings_to_send = Mailing.objects.filter(finished=False,
                                              start_datetime__lte=datetime.now(tz=timezone.utc),
                                              expired=False)

    # DEBUG
    print(f'Что нашли: {mailings_to_send}')

    # проходим по ним и запускаем на отправку, если они не просрочены
    for mailing in mailings_to_send:
        if mailing.stop_datetime > datetime.now(tz=timezone.utc) and not mailing.expired:
            send_mails(mailing)

        # если просрочены - помечаем, чтобы больше не трогать
        elif mailing.stop_datetime <= datetime.now(tz=timezone.utc) and not mailing.expired:
            mailing.expired = True
            mailing.save()


# таск по на e-mail раз в сутки стартовавших рассылок
@shared_task()
def send_finished_mailings():
    """
    раз в сутки отправляет статистику по обработанным рассылкам на email
    """

    # собираем стартовавшие рассылки за сутки
    last_mailings = Mailing.objects.filter(start_datetime__gte=datetime.now(tz=timezone.utc) - timedelta(days=1))

    subject = 'За прошедшие сутки было отправлено несколько рассылок'
    text_message = 'За прошедшие сутки было отправлено несколько рассылок'

    # рендерим в строку шаблон письма и передаём туда переменные, которые в нём используем
    render_html_template = render_to_string('send_mailings.html',
                                            {'mailings': last_mailings,
                                             'subject': subject,
                                             'text_message': text_message})

    # формируем письмо
    mail_admins(subject=subject, message=text_message, html_message=render_html_template)



