from django.core.validators import RegexValidator
from django.db import models
from datetime import datetime


# Сущность "рассылка"
from django.utils import timezone


class Mailing(models.Model):
    start_datetime = models.DateTimeField()  # дата и время запуска рассылки (формат: yyyy-mm-dd HH:MM:SS.mcs)
    text = models.TextField()  # текст сообщения для доставки клиенту
    stop_datetime = models.DateTimeField()  # дата и время окончания рассылки
    finished_datetime = models.DateTimeField(blank=True, null=True)  # дата и время завершения (для статистики)
    tags = models.ManyToManyField('Tag', related_name='mailings', blank=True)  # фильтр тегов клиентов для рассылки
    operators = models.ManyToManyField('Operator', related_name='mailings', blank=True)  # фильтр операторов клиентов для рассылки
    finished = models.BooleanField(default=False)  # рассылка завершена? все сообщения отправлены?
    expired = models.BooleanField(default=False)  # рассылка просрочена?
    # messages - FK

    @property
    def duration(self):
        return (
            None if self.start_datetime > datetime.now(tz=timezone.utc) else
            self.finished_datetime - self.start_datetime if self.finished and not self.expired else
            self.stop_datetime - self.start_datetime if not self.finished and self.expired else
            datetime.now(tz=timezone.utc) - self.start_datetime if not self.finished and not self.expired else
            None
        )

    @property
    def unsended_messages(self):
        return len(self.messages.filter(sended=False))

    @property
    def sended_messages(self):
        return len(self.messages.filter(sended=True))

    @property
    def created_messages(self):
        return len(self.messages.all())


# Сущность "клиент"
class Client(models.Model):
    phone_regex = RegexValidator(regex=r'^7\d{10}$',  # Валидатор номера телефона клиента
                                 message="Номер телефона должен быть в формате 7XXXXXXXXXX (X - цифры от 0 до 9)")
    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)  # номер телефона клиента
    utc_regex = RegexValidator(regex=r'^[+-]?([01]\d?)|(\d)',  # валидатор часового пояса клиента
                               message='Часовой пояс должен быть в формате "+3", "-10" или "0" итд')
    utc = models.CharField(max_length=3, validators=[utc_regex])  # часовой пояс '+3', '-10', etc
    operator = models.ForeignKey('Operator', on_delete=models.CASCADE, related_name='clients')  # моб. оператор
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='clients', blank=True, null=True)  # тег (произвольная метка)
    # messages - FK

    # переопределяем метод save для автозаполнения поля "Оператор"
    def save(self, *args, **kwargs):
        code = self.phone_number[1:4]  # берём цифры номера с 1 по 3
        self.operator, created = Operator.objects.get_or_create(code=code, defaults={'name': code})  # определяем оператора (если такого ещё нет - создаём)
        super().save()  # сохраняем объект


# Сущность "сообщение" - для логов, сюда складывается конкретный кейс с отправкой
class Message(models.Model):
    STATUS_CHOICES = [('Err', 'Error'), ('OK', 'Sent'), ('New', 'New'), ('BR', 'Bad Request')]
    create_datetime = models.DateTimeField(auto_now_add=True)  # дата и время создания
    sended_datetime = models.DateTimeField(blank=True, null=True)  # дата и время отправки
    sended = models.BooleanField(default=False)  # статус отправки (отправлено?)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='New')
    mailing = models.ForeignKey(Mailing, blank=True, on_delete=models.CASCADE, related_name='messages')  # id рассылки, в рамках которой было отправлено сообщение
    client = models.ForeignKey(Client, blank=True, on_delete=models.CASCADE, related_name='messages')  # id клиента, которому отправили


# сущность "оператор"
class Operator(models.Model):
    name = models.CharField(max_length=50)

    # сейчас у одного оператора - один код,
    # однако, если у оператора может быть несколько кодов есть два варианта:
    #   1 - создать сущность "Код оператора"
    #   2 - если хранить БД в PostgreSQL, то использовать тип поля ArrayField для хранения массива
    code_regex = RegexValidator(regex=r'^\d{3}$',  # Валидатор кода оператора
                                message="Код оператора должен состоять из трёх цифр")
    code = models.CharField(validators=[code_regex], max_length=3, unique=True)
    # clients - FK
    # mailings - FK


# сущность "тег"
class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)
    # clients - FK
    # mailings - FK
