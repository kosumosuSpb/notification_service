from celery import shared_task
from .models import Mailing, Client, Message
from django.db.models import Q
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from datetime import datetime
import json


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
        # args=json.dumps([]),
        kwargs=json.dumps({'mailing_id': mailing_id}),
        expires=mailing.stop_datetime
    )

    print('=== make_mailing task ====>', mailing_task.__dict__)


@shared_task(name='send_mails')
def send_mails(mailing_id):
    """
    Достаёт объект рассылки, из него - теги и операторов
    по ним фильтрует клиентов и запускает рассылку по ним

    :param mailing_id: id рассылки
    :return: None
    """
    # получить клиентов, текст, временной интервал рассылки,
    # пройтись по клиентам и разослать сообщения
    # достаём рассылку
    print(f'=== send_mails task starts === \n=== with mailing id: ===> {mailing_id} <===')
    mailing = Mailing.objects.get(pk=mailing_id)

    # достаём фильтры для рассылки
    tags = mailing.tags.all()
    operators = mailing.operators.all()

    # используем Q-объекты, чтобы искать сразу по двум параметрам с помощью оператора | (OR)
    # получаем кверисет клиентов для рассылки
    clients = Client.objects.filter(Q(tag__in=tags) | Q(operator__in=operators))

    print('===> START send_mails <===')
    print(clients, mailing.text)

    for client in clients:
        # если передать самого клиента, то упадёт в исключение:
        # kombu.exceptions.EncodeError: Object of type Client is not JSON serializable
        send_client.apply_async([client.id, mailing.id])

    print('===> FINISHED send_mails <===')


@shared_task(name='send_client')
def send_client(client_id, mailing_id):
    # отправка сообщения одному клиенту через внешний АПИ сервис c JWT-авторизацией через токен
    # https://probe.fbrq.cloud/v1/send/{msgId}
    # {
    #   "id": 0,
    #   "phone": 0,
    #   "text": "string"
    # }
    client = Client.objects.get(pk=client_id)
    mailing = Mailing.objects.get(pk=mailing_id)
    print('---> START send_client <---')
    print(client, mailing)
    message = Message.objects.create(mailing=mailing, client=client)
    message.save()
    print(f'--- Message {message.id} created: {message.__dict__} --- ')
    print('--- API send here --- ')
    # здесь нужно сделать отправку и проверку ответа и if
    message.sended_datetime = datetime.now()
    message.sended = True
    message.save()
    print(f'--- Message {message.id} sended: {message.__dict__} --- ')
