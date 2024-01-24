from rest_framework import serializers

from .models import Chat, Message
from ...users import models as user_models


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields: list[str] = [
            'id', 'username'
        ]


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields: list[str] = ['id']


class MessageSerializer(serializers.ModelSerializer):
    sender = ChatUserSerializer()
    receiver = ChatUserSerializer()

    class Meta:
        model = Message
        fields: str = '__all__'
