from rest_framework import serializers
from .models import *


class MailingSerializer(serializers.ModelSerializer):
    """
    сериалайзер для рассылок
    """
    class Meta:
        model = Mailing
        fields = ['id', 'start_datetime', 'stop_datetime', 'text', 'tags', 'operators']


class MailingStatSerializer(serializers.ModelSerializer):
    """
    сериалайзер для статистики по рассылкам
    """
    class Meta:
        model = Mailing
        fields = [
            'id', 'text', 'tags', 'operators',
            'start_datetime', 'finished_datetime', 'stop_datetime',
            'duration', 'expired',
            'created_messages', 'sent_messages', 'unsent_messages',
        ]


class ClientSerializer(serializers.ModelSerializer):
    """
    сериалайзер для клиентов
    """
    class Meta:
        model = Client
        # fields = '__all__'
        exclude = ['operator']


class MessageSerializer(serializers.ModelSerializer):
    """
    сериалайзер для сообщений
    """
    class Meta:
        model = Message
        fields = '__all__'


class OperatorSerializer(serializers.ModelSerializer):
    """
    сериалайзер для операторов
    """
    class Meta:
        model = Operator
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """
    сериалайзер для тегов
    """
    class Meta:
        model = Tag
        fields = '__all__'
