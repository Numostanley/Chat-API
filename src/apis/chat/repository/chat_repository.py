from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from ...users.models import User
from ..entity.models import Chat, Message
from ...users.db_queries import base as user_db_queries
from ..db_queries import base as chat_db_queries


class ChatRepository:
    @staticmethod
    def create_chat(user: User, target_user_id: str) -> Chat | None:
        if not user_db_queries.get_user_by_id(target_user_id):
            return None

        target_user = get_object_or_404(User, id=target_user_id)
        existing_chat = Chat.objects.filter(  # noqa
            participants__in=[user, target_user]
        ).filter(
            participants__in=[target_user, user]
        ).first()

        if existing_chat:
            return existing_chat

        new_chat = Chat.objects.create()  # noqa
        new_chat.participants.add(user)
        new_chat.participants.add(target_user)
        return new_chat

    @staticmethod
    def get_existing_chats(user):
        existing_chat = Chat.objects.filter( # noqa
            Q(participants=user)
        )
        return existing_chat

    @staticmethod
    def send_message(chat_id: str, sender_id: str, content: str, attachment):
        chat = chat_db_queries.get_chat_by_id(chat_id)
        sender = user_db_queries.get_user_by_id(sender_id)
        if chat is not None and sender is not None:
            message = Message.objects.create(  # noqa
                chat=chat, sender=sender,
                content=content, attachment=attachment
            )
            return message
        else:
            return None

    @staticmethod
    def list_messages(chat_id: str):
        messages = chat_db_queries.get_messages_by_chat_id(chat_id)
        if messages.count() > 0:
            return messages
        return None

    @staticmethod
    def read_message(message_id, user_id):
        try:
            message = chat_db_queries.get_message_by_id(message_id)
            if message is None or user_id != message.receiver.id:
                return None
            message.is_read = True
            message.read_time = timezone.now()
            message.save()
            return message
        except ObjectDoesNotExist:
            pass

    @staticmethod
    def read_messages(chat_id: str, user_id: str):
        messages = chat_db_queries.get_messages_by_receiver(user_id, chat_id)
        if messages.count() > 0:
            for message in messages:
                message.is_read = True
                message.read_time = timezone.now()
                message.save()
            return messages
