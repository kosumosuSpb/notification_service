from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class MailingViewSet(viewsets.ModelViewSet):
    """
    Используется вьюсет, который автоматически предоставляет методы
    `list`, `create`, `retrieve`, `update` and `destroy` для модели Рассылка
    """
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

    # вывод статистики по отдельной рассылке
    @action(detail=True)
    def stat(self, request, pk=None):
        """
        Статистика по объекту конкретной рассылки
        показывает продолжительность рассылки, сколько сообщений создано, сколько удалось отправить
        """
        queryset = Mailing.objects.all()
        mailing = get_object_or_404(queryset, pk=pk)
        serializer = MailingStatSerializer(mailing)
        return Response(serializer.data)

    # вывод статистики по всем рассылкам
    @action(detail=False)
    def allstat(self, request):
        """
        Выводит список всех рассылок со статистикой по каждой

        """
        queryset = Mailing.objects.all()
        serializer = MailingStatSerializer(queryset, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    """
    Используется вьюсет, который автоматически предоставляет методы
    `list`, `create`, `retrieve`, `update` and `destroy` для модели Клиент
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    Используется вьюсет, который автоматически предоставляет методы
    `list`, `create`, `retrieve`, `update` and `destroy` для модели Сообщение
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class OperatorViewSet(viewsets.ModelViewSet):
    """
    Используется вьюсет, который автоматически предоставляет методы
    `list`, `create`, `retrieve`, `update` and `destroy` для модели Оператор
    """
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    Используется вьюсет, который автоматически предоставляет методы
    `list`, `create`, `retrieve`, `update` and `destroy` для модели Тег
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
