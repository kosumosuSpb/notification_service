from django.test import TestCase
from notifications import models
import logging


logger = logging.getLogger(__name__)


class BaseNotificationsTests(TestCase):
    @staticmethod
    def create_test_fixtures():
        try:
            # создаём тестовые объекты и сохраняем их в БД
            tag1 = models.Tag(name='tag1')
            tag1.save()
            tag2 = models.Tag(name='tag2')
            tag2.save()
            tag3 = models.Tag(name='tag3')
            tag3.save()

            models.Operator(name='MTS', code='911').save()
            models.Operator(name='Megafon', code='921').save()

            models.Client(phone_number='79119876543', utc='+3', tag=tag1).save()
            models.Client(phone_number='79119876544', utc='0').save()
            models.Client(phone_number='79219876543', utc='-2', tag=tag2).save()
            models.Client(phone_number='79215554422', utc='-5', tag=tag3).save()

        # если какая-то ошибка - выводим её
        except Exception as e:
            logger.error(f'Ошибка: {e}')

    def test_index_loads(self):
        """Проверяет доступность страницы root"""
        response = self.client.get('http://127.0.0.1:8000/')
        self.assertEqual(response.status_code, 200)

    def test_mailngs_loads(self):
        """Проверяет доступность страницы mailings"""
        # создаём тестовые объекты
        BaseNotificationsTests.create_test_fixtures()

        response = self.client.get('http://127.0.0.1:8000/mailings/')
        self.assertEqual(response.status_code, 200)

    def test_clients_loads(self):
        """Проверяет доступность страницы clients"""
        # создаём тестовые объекты
        BaseNotificationsTests.create_test_fixtures()

        response = self.client.get('http://127.0.0.1:8000/clients/')
        self.assertEqual(response.status_code, 200)

    def test_operators_loads(self):
        """Проверяет доступность страницы operators"""
        # создаём тестовые объекты
        BaseNotificationsTests.create_test_fixtures()

        response = self.client.get('http://127.0.0.1:8000/operators/')
        self.assertEqual(response.status_code, 200)

    def test_tags_loads(self):
        """Проверяет доступность страницы tags"""
        # создаём тестовые объекты
        BaseNotificationsTests.create_test_fixtures()

        response = self.client.get('http://127.0.0.1:8000/tags/')
        self.assertEqual(response.status_code, 200)

    def test_client_operator_defined(self):
        """Проверка определения оператора для клиента"""
        # создаём тестовые объекты
        BaseNotificationsTests.create_test_fixtures()

        client = models.Client.objects.get(pk=1)
        self.assertIsInstance(client.operator, models.Operator)
