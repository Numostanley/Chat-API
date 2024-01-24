from ..service.chat_service import ChatService
from ..entity.serializers import ChatSerializer, MessageSerializer
from ...users.models import User
from ...base import responses as base_repo_responses, views as base_repo_views


class ChatAPIView(base_repo_views.UserAuthenticationAPIView):
    def get(self, request):  # noqa
        try:
            user_id: str = self.request.user_id

            user = User.objects.get(id=user_id)
            chat_service = ChatService()
            chats = chat_service.get_chat(user)

            serializer = ChatSerializer(chats, many=True)
            return base_repo_responses.http_response_200(
                'Chat retrieved successfully!', data=self.paginate_response(serializer.data, request)
            )
        except Exception as e:
            self._log.error('ChatAPIView.get@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)

    def post(self, request):
        try:
            data: dict = request.data
            target_user_id: str = data.get('target_user_id')
            user_id: str = self.request.user_id

            user = User.objects.get(id=user_id)
            chat_service = ChatService()
            chat = chat_service.create_chat(user, target_user_id)

            serializer = ChatSerializer(chat)
            return base_repo_responses.http_response_200(
                'Chat created successfully!', data=serializer.data
            )
        except Exception as e:
            self._log.error('ChatAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)


class MessageAPIView(base_repo_views.UserAuthenticationAPIView):

    def post(self, request, chat_id):  # noqa
        try:
            data: dict = request.data
            sender_id: str = request.user_id
            content: str = data.get('message')
            attachment = request.FILES.get('attachment', None)

            chat_service = ChatService()
            message = chat_service.send_message(chat_id, sender_id, content, attachment)
            if message is not None:
                serializer = MessageSerializer(message)
                return base_repo_responses.http_response_200(
                    'Message sent successfully!', data=serializer.data
                )
            else:
                return base_repo_responses.http_response_404(
                    'Invalid chat_id!'
                )
        except Exception as e:
            self._log.error('MessageAPIView.post@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)

    def get(self, request, chat_id):  # noqa
        try:
            chat_service = ChatService()
            messages = chat_service.list_messages(chat_id)
            if messages is not None:
                serializer = MessageSerializer(messages, many=True)
                return base_repo_responses.http_response_200(
                    'Messages retrieved successfully!', data=self.paginate_response(serializer.data, request)
                )
            else:
                return base_repo_responses.http_response_404(
                    'Invalid chat_id!'
                )
        except Exception as e:
            self._log.error('MessageAPIView.get@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)

    def put(self, request, message_id):
        try:
            chat_service = ChatService()
            message = chat_service.read_message(message_id, request.user_id)
            if message is not None:
                serializer = MessageSerializer(message)
                return base_repo_responses.http_response_200(
                    'Messages read successfully!', data=serializer.data
                )
            else:
                return base_repo_responses.http_response_404(
                    'Invalid reader or message_id'
                )
        except Exception as e:
            self._log.error('MessageAPIView.put@Error')
            self._log.error(e)
            return base_repo_responses.http_response_500(self.server_error_msg)