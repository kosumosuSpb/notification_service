from django.core.management.base import BaseCommand, CommandError
from notifications.models import *


class Command(BaseCommand):
    # показывает подсказку при вводе "python manage.py <команда> --help"
    help = 'Добавляет тестовые объекты в БД: теги, операторы и клиенты'
    # missing_args_message = 'Недостаточно аргументов'

    # напоминать ли о миграциях.
    # Если true — то будет напоминание о том, что не сделаны все миграции (если такие есть)
    requires_migrations_checks = True

    def handle(self, *args, **options):
        answer = input(f'Создать тестовые объекты в БД? yes/no > ')

        # если не да:
        if answer not in ('yes', 'y'):
            self.stdout.write(self.style.ERROR('Отменено'))
            return

        try:
            # создаём объекты и сохраняем их в БД
            tag1 = Tag(name='tag1')
            tag1.save()
            tag2 = Tag(name='tag2')
            tag2.save()
            tag3 = Tag(name='tag3')
            tag3.save()

            Operator(name='MTS', code='911').save()
            Operator(name='Megafon', code='921').save()

            Client(phone_number='79119876543', utc='+3', tag=tag1).save()
            Client(phone_number='79119876544', utc='0').save()
            Client(phone_number='79219876543', utc='-2', tag=tag2).save()
            Client(phone_number='79215554422', utc='-5', tag=tag3).save()

        # если какая-то ошибка - выводим её
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))

        else:
            # если всё ок - выводим сообщение с инфой о том, что создалось
            self.stdout.write(self.style.SUCCESS(
                f'Теги: {Tag.objects.all()}, \n'
                f'Операторы: {Operator.objects.all()}, \n'
                f'Клиенты: {Client.objects.all()}'
            ))
