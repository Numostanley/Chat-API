import base64
import json
import secrets

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.utils import timezone

from .entity.models import Message, Chat
from .entity.serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_name = None
        self.chat_id = None

    def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.chat_name = f"chat_{self.chat_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.chat_name, self.channel_name  # noqa
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_name, self.channel_name  # noqa
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json: dict = json.loads(text_data)

        if "read_message" == text_data_json.get("type"):
            self.read_message_ws(text_data_json)
        else:
            sender = self.scope['user']
            chat_id = self.chat_id
            message: str = text_data_json.get("message")
            attachment = text_data_json.get("attachment")

            chat = Chat.objects.get(id=chat_id)  # noqa

            participants = chat.participants.all()
            receiver = [user for user in participants if user != sender][0] if participants else None

            if attachment:
                file_str, file_ext = attachment["data"], attachment["format"]
                file_data = ContentFile(
                    base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
                )
                _message = Message.objects.create(  # noqa
                    sender=sender,
                    attachment=file_data,
                    content=message,
                    chat=chat,
                    receiver=receiver
                )
            else:
                _message = Message.objects.create(  # noqa
                    sender=sender,
                    content=message,
                    chat=chat,
                    receiver=receiver
                )

            serializer = MessageSerializer(instance=_message)
            async_to_sync(self.channel_layer.group_send)(
                self.chat_name,
                    {'type': 'chat_message', 'message': serializer.data}  # noqa
            )

    def chat_message(self, event):
        message_data: dict = event.get("message")
        self.send(
            text_data=json.dumps({
                'type': 'chat_message',
                'message': message_data,
            })
        )

    def read_message_ws(self, event):
        message_id: str = event.get("message_id")
        user_id = self.scope["user"].id
        try:
            message = Message.objects.get(id=message_id)  # noqa
            if user_id != message.receiver.id:
                self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid user',
                }))
                return
            if message.is_read:
                self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Message already read',
                }))
                return

            message.is_read = True
            message.read_time = timezone.now()
            message.save()
            async_to_sync(self.channel_layer.group_send)(
                self.chat_name,
                {  # noqa
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'status': "read",
                    'time': message.read_time.__str__()
                }
            )
        except ObjectDoesNotExist:
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message not found.',
            }))

    def read_receipt(self, event):
        message_id: str = event.get("message_id")
        status: str = event.get("status")
        time: str = event.get("time")

        self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': message_id,
            'status': status,
            'time': time
        }))
