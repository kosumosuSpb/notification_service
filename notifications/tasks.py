from celery import shared_task
from .models import Mailing, Client, Message
from django.db.models import Q
from datetime import datetime
import json
import requests


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
    print(f'=== send_mails task starts === with mailing id: ===> {mailing.id} <===')

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
    print(f'Finished: {finished}')

    mailing.finished = True if finished else False
    mailing.save()


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
    TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzYxNDQ2NzMsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6ImtvbnN0YW50aW4uY2hlcm5vdiJ9.yx543hnuCBuib8ZlWmtmYq7EanWLAHwdkp7zYtd9dq8'

    # создаём экземпляр сообщения для отчётов
    # если он уже существует, то просто извлекаем из БД
    message, created = Message.objects.get_or_create(mailing=mailing, client=client)

    if created:
        message.save()

    # DEBUG
    print(f'--- Message {message.id} created: {message.__dict__} --- ')

    # DEBUG
    print('---> START send_client <---')
    print(client, mailing)

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

    try:
        # отправляем данные, принимаем ответ, ждём 5 секунд
        response = requests.post(url=url + message.id, data=data, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f'HTTPError: {e}')
        return False
    except Exception as e:
        print(f'Ошибка: {e}')
        return False
    else:
        if response.status_code == requests.codes.ok:
            # Отмечаем, что отправка прошла успешно
            message.sended_datetime = datetime.now()
            message.sended = True
            message.save()

            # DEBUG
            print(f'--- Message {message.id} sended: {message.__dict__} --- ')

            return True


    # DEBUG #
    print(f'Cant send Mailing {mailing.id}, response is: {response}')
    return False


# таск для перебора рассылок и отправки не отправленных
@shared_task()
def check_and_send():
    """
    Перебирает рассылки и рассылает те, которые уже нужно и которые не просрочены

    :return:
    """
    # собираем не отправленные рассылки, которые уже пора отправлять
    mailings_to_send = Mailing.objects.filter(finished=False, start_datetime__lte=datetime.now(), expired=False)

    # проходим по ним и запускаем на отправку, если они не просрочены
    for mailing in mailings_to_send:
        if mailing.stop_datetime > datetime.now():
            send_mails(mailing)
        # если просрочены - помечаем, чтобы больше не трогать
        else:
            mailing.expired = True
            mailing.save()
