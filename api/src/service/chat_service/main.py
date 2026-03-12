from src.model.dto.request import ChatQueryDTO
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableLambda
from src.model.schema.chat_schema import ChatMessage
from src.dao import chat_dao
from .router.main import dialogue_manager
from fastapi.responses import StreamingResponse
from src.config import setup_logging

logger = setup_logging()


class ChatService:
    def __init__(self):

        self.chat_dao = chat_dao

    async def chat(self, dto: ChatQueryDTO, chat_history: list, extra_context: str):
        async for chunk in dialogue_manager.process(dto, chat_history, extra_context):
            yield chunk

    def create_conversation(self, user_id: str, conv_title: str):
        return self.chat_dao.create_conversation(user_id, conv_title)

    def get_conversation_detail(self, conv_id: str):
        return self.chat_dao.get_conversation_detail(conv_id)

    def get_conversation_list(self, user_id: str):
        return self.chat_dao.get_conversation_list(user_id)


chat_service = ChatService()
