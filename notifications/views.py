from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class MailingViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for Mailing model
    """
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

    # вывод статистики по отдельной рассылке
    @action(detail=True)
    def stat(self, request, pk=None):
        queryset = Mailing.objects.all()
        mailing = get_object_or_404(queryset, pk=pk)
        serializer = MailingStatSerializer(mailing)
        return Response(serializer.data)

    # вывод статистики по всем рассылкам
    @action(detail=False)
    def allstat(self, request):
        queryset = Mailing.objects.all()
        serializer = MailingStatSerializer(queryset, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for Client model
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for Message model
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class OperatorViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for Operator model
    """
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for Tag model
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
