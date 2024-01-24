from django.urls import path
from .views import ChatAPIView, MessageAPIView


app_name: str = "chat"

urlpatterns = [
    path('', ChatAPIView.as_view()),
    path('messages/<chat_id>', MessageAPIView.as_view())
]
