import os
from celery import Celery
from celery.schedules import crontab
from celery import shared_task
from django.conf import settings


# этот код скопирован с manage.py
# он установит модуль настроек по умолчанию Django для приложения 'celery'.
# notification_service.settings - имя_проекта.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')

# Создаем объект (экземпляр класса) celery и даем ему имя
# celery -A notification_service worker -l info -P eventlet
# celery -A notification_service beat -l INFO
# запускать из под папки проекта, выше сеттингзов
app = Celery('notification_service')

# Загружаем config с настройками для объекта celery.
# т.е. импортируем настройки из django файла settings
# namespace='CELERY' - в данном случае говорит о том, что применятся будут только
# те настройки из файла settings.py которые начинаются с ключевого слова CELERY
app.config_from_object('django.conf:settings', namespace="CELERY")
