from celery import shared_task
from .models import Mailing, Client
from django.db.models import Q


@shared_task()
def test_task():
    print('=== its the test task --->')


@shared_task()
def send_mails(mailing, clients):
    # получить клиентов, текст, временной интервал рассылки,
    # пройтись по клиентам и разослать сообщения
    #


    pass


@shared_task()
def send_client(client):
    # отправка сообщения одному клиенту через внешний АПИ сервис c JWT-авторизацией через токен
    # https://probe.fbrq.cloud/v1/send/{msgId}
    # {
    #   "id": 0,
    #   "phone": 0,
    #   "text": "string"
    # }
    pass


@shared_task()
def make_mailing(mailing_id, *args, **kwargs):
    """
    Создаёт рассылку, как периодическую задачу, используя id рассылки
    достаёт рассылку, вытаскивает клиентов по тегам и операторам.

    :param mailing_id: id объекта рассылки
    :return: None
    """
    # достаём рассылку
    instance = Mailing.objects.get(pk=mailing_id)

    # достаём фильтры для рассылки
    tags = instance.tags.all()
    operators = instance.operators.all()

    # используем Q-объекты, чтобы искать сразу по двум параметрам с помощью оператора | (OR)
    # получаем кверисет клиентов для рассылки
    clients_to_mailing = Client.objects.filter(Q(tag__in=tags) | Q(operator__in=operators))

    # создание таска на рассылку
    print('===make_mailing task====>', clients_to_mailing)
