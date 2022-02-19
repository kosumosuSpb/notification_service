from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics, viewsets
from rest_framework.renderers import JSONRenderer


class MailingViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for Mailing model
    """
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer
    # renderer_classes = [JSONRenderer]  # если закомментировать, отрендерится html версия ответа


class ClientViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions for Client model
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    # renderer_classes = [JSONRenderer]  # если закомментировать, отрендерится html версия ответа


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
