from celery import shared_task
from .models import Mailing, Client
from django.db.models import Q
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from datetime import datetime


@shared_task()
def make_mailing(mailing_id, *args, **kwargs):
    """
    Создаёт рассылку, как периодическую задачу, используя id рассылки
    достаёт рассылку, вытаскивает клиентов по тегам и операторам.

    :param mailing_id: id объекта рассылки
    :return: None
    """
    # достаём рассылку
    mailing = Mailing.objects.get(pk=mailing_id)

    # достаём фильтры для рассылки
    tags = mailing.tags.all()
    operators = mailing.operators.all()

    # используем Q-объекты, чтобы искать сразу по двум параметрам с помощью оператора | (OR)
    # получаем кверисет клиентов для рассылки
    clients_to_mailing = Client.objects.filter(Q(tag__in=tags) | Q(operator__in=operators))

    # расписание запуска таска
    schedule = CrontabSchedule.objects.create(
        minute=mailing.start_datetime.minute,
        hour=mailing.start_datetime.hour,
        # day_of_week='*',
        day_of_month=mailing.start_datetime.day,
        month_of_year=mailing.start_datetime.month,
    )

    # создание таска на рассылку
    mailing_task = PeriodicTask.objects.create(
        crontab=schedule,
        name=f'Mailing task {mailing.id}',
        task='send_mails',
        args=[clients_to_mailing, mailing.text],
        # kwargs={'clients': clients_to_mailing, 'text': mailing.text},
        expires=mailing.stop_datetime
    )

    print('=== make_mailing task ====>', mailing_task.__dict__)
    print('=== make_mailing clients ====>', clients_to_mailing)


@shared_task()
def send_mails(clients, text, *args):
    # получить клиентов, текст, временной интервал рассылки,
    # пройтись по клиентам и разослать сообщения

    print('===> START send_mails <===')

    for client in clients:
        send_client.apply_async([client, text])

    print('===> FINISHED send_mails <===')


@shared_task()
def send_client(client, text):
    # отправка сообщения одному клиенту через внешний АПИ сервис c JWT-авторизацией через токен
    # https://probe.fbrq.cloud/v1/send/{msgId}
    # {
    #   "id": 0,
    #   "phone": 0,
    #   "text": "string"
    # }
    print('===> START send_client <===')
    print(client, text)

