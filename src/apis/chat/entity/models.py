from django.db import models

from ...users.models import User
from . import model_helpers as chat_model_helpers


class Chat(models.Model):
    id = models.CharField(primary_key=True, default=chat_model_helpers.generate_chat_id, db_index=True,
                          max_length=60, editable=False, unique=True)
    participants = models.ManyToManyField(User, related_name='chats')


class Message(models.Model):
    id = models.CharField(primary_key=True, default=chat_model_helpers.generate_message_id, db_index=True,
                          max_length=60, editable=False, unique=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_time = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)

    class Meta:
        ordering = ('-timestamp',)
