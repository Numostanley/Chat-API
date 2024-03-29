from django.db.models import Count

from ..entity import models as chat_models


def get_chat_by_id(chat_id: str):
    try:
        return chat_models.Chat.objects.get(id=chat_id)   # noqa
    except (Exception, chat_models.Chat.DoesNotExist):  # noqa
        return None


def get_messages_by_chat_id(chat_id: str):
    return chat_models.Message.objects.filter(chat_id=chat_id)  # noqa


def get_message_by_id(message_id: str):
    try:
        return chat_models.Message.objects.get(id=message_id)  # noqa
    except (Exception, chat_models.Message.DoesNotExist):  # noqa
        return None


def get_messages_by_receiver(receiver_id: str, chat_id: str):
    return chat_models.Message.objects.filter(  # noqa
        receiver_id=receiver_id,
        chat_id=chat_id,
        is_read=False
    )
