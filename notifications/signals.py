from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, m2m_changed
from .models import Client
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Client)
def client_logging(created, instance, **kwargs):
    """Логгирование создания и изменений объекта клиента"""
    if created:
        logger.info(f'Клиент {instance.id} создан')
    else:
        logger.info(f'Клиент {instance} изменён')


@receiver(post_delete, sender=Client)
def client_logging(instance, **kwargs):
    """Логгирование удаления объекта клиента"""
    logger.info(f'Клиент {instance.id} удалён')
