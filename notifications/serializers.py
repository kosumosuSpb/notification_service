from rest_framework import serializers
from .models import *


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = ['id', 'start_datetime', 'stop_datetime', 'text', 'tags', 'operators']


class MailingStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = [
            'id', 'text', 'tags', 'operators',
            'start_datetime', 'finished_datetime', 'stop_datetime',
            'duration',
            'created_messages', 'sended_messages', 'unsended_messages',
        ]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        # fields = '__all__'
        exclude = ['operator']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
