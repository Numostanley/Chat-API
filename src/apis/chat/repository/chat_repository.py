from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from ...users.models import User
from ..entity.models import Chat, Message
from ...users.db_queries import base as user_db_queries


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
        try:
            chat = Chat.objects.get(id=chat_id)  # noqa
            sender = User.objects.get(id=sender_id)  # noqa
            message = Message.objects.create(  # noqa
                chat=chat, sender=sender,
                content=content, attachment=attachment
            )
            return message
        except ObjectDoesNotExist:
            pass

    @staticmethod
    def list_messages(chat_id: str):
        try:
            chat = Chat.objects.get(id=chat_id)  # noqa
            return Message.objects.filter(chat=chat)  # noqa
        except ObjectDoesNotExist:
            pass

    @staticmethod
    def read_message(message_id, user_id):
        try:
            message = Message.objects.get(id=message_id)  # noqa
            if user_id != message.receiver.id:
                return None
            message.is_read = True
            message.read_time = timezone.now()
            message.save()
            return message
        except ObjectDoesNotExist:
            pass
