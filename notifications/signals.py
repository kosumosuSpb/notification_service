from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from .models import Mailing
from .tasks import make_mailing


# сигнал на создание таска на рассылку в селери при сохранении модели рассылки
@receiver(post_save, sender=Mailing)
def create_mailing(**kwargs):
    instance = kwargs['instance']  # объект Mailing
    created = kwargs['created']  # Bool

    # таск на создание периодической рассылки по переданному id
    # чтобы вытащить его из БД уже со всеми связями с помощью селери
    make_mailing.delay(instance.id)
