from celery import shared_task
from .models import Mailing, Client, Message
from django.db.models import Q
from datetime import datetime, timedelta
import json
import requests
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import mail_admins
import logging


# Создаём логгер
logger = logging.getLogger(__name__)


def send_mailing(mailing):
    """
    Отправка рассылки

    Принимает объект рассылки, из него - теги и операторов
    по ним фильтрует клиентов и запускает рассылку по ним.

    Если всё отправилось и вернуло ответ True,
    то рассылка помечается, как finished = True

    :param mailing: объект рассылки
    :return: None
    """
    # проверяем, запускалась ли уже рассылка:
    # если сообщения уже есть, то запускалась,
    # надо попробовать переслать те, что не получилось
    if mailing.messages.exists():
        logger.info(f'Повторная отправка рассылки {mailing.id}...')

        finished = all([send_client(message.client, mailing)
                        for message in mailing.messages.all()
                        if message.sent is False])

    # если сообщений нет, то рассылка ещё не запускалась,
    # формируем её
    else:
        logger.info(f'Создание рассылки {mailing.id}...')

        # достаём фильтры для рассылки
        tags = mailing.tags.all()
        operators = mailing.operators.all()

        # используем Q-объекты, чтобы искать сразу по двум параметрам с помощью оператора | (OR)
        # получаем кверисет клиентов для рассылки
        clients = Client.objects.filter(Q(tag__in=tags) | Q(operator__in=operators))

        logger.debug(f'Клиенты на отправку: {clients}')

        # перебор клиентов, запуск рассылки по ним и возврат ответов:
        # если все True, то рассылка завершена и её можно закрывать
        finished = all([send_client(client, mailing) for client in clients])

    # если всё отправилось, то отмечаем рассылку, как завершённая
    if finished:
        mailing.finished = True
        mailing.finished_datetime = datetime.now(tz=timezone.utc)
        mailing.save()

        logger.info(f'Рассылка {mailing.id} завершена {mailing.finished_datetime}')

    else:
        logger.info(f'Рассылка {mailing.id} не завершена')


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
    # в проде должен быть в отдельном файле, а файл - в гитигноре
    TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzYxNDQ2NzMsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6ImtvbnN0YW50aW4uY2hlcm5vdiJ9.yx543hnuCBuib8ZlWmtmYq7EanWLAHwdkp7zYtd9dq8'

    # создаём экземпляр сообщения для отчётов
    # если он уже существует, то просто извлекаем из БД
    message, created = Message.objects.get_or_create(mailing=mailing, client=client)

    if created:
        message.save()
        logger.info(f'Сообщение {message.id} создано')

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
        # отправляем данные, ждём ответа 5 секунд
        response = requests.post(url=url + str(message.id), data=data, headers=headers, timeout=5)

        # DEBUG
        logger.debug(response)

        response.raise_for_status()

    # исключения можно конкретизировать, если нужно
    except Exception as e:
        logger.warning(f'Ошибка: {e}')
        return False
    else:
        if response.status_code == requests.codes.ok:
            # Отмечаем, что отправка прошла успешно
            message.sent_datetime = datetime.now(tz=timezone.utc)
            message.sent = True
            message.save()
            logger.info(f'Сообщение {message.id} отправлено')
            return True


# таск для перебора рассылок и отправки не отправленных
@shared_task()
def check_and_send():
    """
    Перебирает рассылки и рассылает те, которые уже нужно и которые не просрочены
    помечает те, которые просрочены
    """
    # собираем не отправленные рассылки, которые уже пора отправлять
    mailings_to_send = Mailing.objects.filter(finished=False,
                                              start_datetime__lte=datetime.now(tz=timezone.utc),
                                              expired=False)

    # проходим по ним и запускаем на отправку, если они не просрочены
    for mailing in mailings_to_send:
        if mailing.stop_datetime > datetime.now(tz=timezone.utc):
            send_mailing(mailing)

        # если просрочены - помечаем, чтобы больше не трогать
        elif mailing.stop_datetime <= datetime.now(tz=timezone.utc):
            mailing.expired = True
            mailing.save()


# таск отправки стартовавших рассылок на e-mail раз в сутки
@shared_task()
def send_starting_mailings():
    """
    раз в сутки отправляет статистику по обработанным рассылкам на email
    """
    logger.info('Собираем рассылки за сутки')

    # собираем стартовавшие рассылки за сутки
    last_mailings = Mailing.objects.filter(start_datetime__gte=datetime.now(tz=timezone.utc) - timedelta(days=1))
    logger.debug(f'Собранные рассылки: {last_mailings}')

    subject = 'За прошедшие сутки было запущено несколько рассылок'
    text_message = 'За прошедшие сутки было запущено несколько рассылок'

    # рендерим в строку шаблон письма и передаём туда переменные, которые в нём используем
    render_html_template = render_to_string('send_mailings.html',
                                            {'mailings': last_mailings,
                                             'subject': subject,
                                             'text_message': text_message})

    # формируем и отправляем письмо
    # в письме будет простой HTML со ссылками на рассылки
    mail_admins(subject=subject, message=text_message, html_message=render_html_template)
    logger.info('Отправляем рассылки на почту')
