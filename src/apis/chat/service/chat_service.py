from ..repository.chat_repository import ChatRepository


class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()

    def create_chat(self, user, target_user_id: str):
        return self.chat_repository.create_chat(user, target_user_id)

    def get_chat(self, user):
        return self.chat_repository.get_existing_chats(user)

    def send_message(self, chat_id: str, sender_id: str, content: str, attachment):
        return self.chat_repository.send_message(chat_id, sender_id, content, attachment)

    def list_messages(self, chat_id: str):
        return self.chat_repository.list_messages(chat_id)

    def read_message(self, message_id: str, user_id):
        return self.chat_repository.read_message(message_id, user_id)
