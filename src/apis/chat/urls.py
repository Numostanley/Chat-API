from django.urls import path
from .views import ChatAPIView, MessageAPIView, ReadMessageAPIView


app_name: str = "chat"

urlpatterns = [
    path('', ChatAPIView.as_view()),
    path('messages/<chat_id>', MessageAPIView.as_view()),
    path('read/<message_id>', ReadMessageAPIView.as_view())
]
