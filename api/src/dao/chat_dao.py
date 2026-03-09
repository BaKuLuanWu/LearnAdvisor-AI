from src.infra.vector_store import course_vector_store
from src.infra.sql_db.repo import message_repo, conv_repo, hot_question_repo
from src.model.schema.chat_schema import ChatMessage
from src.config.settings import setup_logging
import asyncio

logger = setup_logging()


class ChatDao:

    def __init__(self):

        self.course_vector_store = course_vector_store

        self.hot_question_repo = hot_question_repo
        self.msg_repo = message_repo
        self.conv_repo = conv_repo

    def get_documents(self, user_input: str) -> list[dict]:
        return self.course_vector_store.search(user_input)

    def save_round_of_conv(self, conv_id: str, turn: list[ChatMessage]):
        for msg in turn:
            self.msg_repo.add_message(conv_id, msg)
        self.conv_repo.update_conversation(conv_id)
        logger.info("新对话保存成功！")

    def create_conversation(self, user_id: str, title: str):
        conv_id = self.conv_repo.create_conversation(user_id=user_id, title=title)

        return conv_id

    def get_conversation_detail(self, conv_id: str):
        conv = self.conv_repo.get_by_id(conv_id=conv_id)
        
        if conv:
            print("-------------------")
            logger.info(f"对话{conv['conv_id']} {conv['title']}")
            print("-------------------")
        else:
            print("-------------------")
            logger.error("对话不存在")
            print("-------------------")
        return conv

    def get_conversation_list(self, user_id: str):
        conv_list = self.conv_repo.get_conversation_list(user_id=user_id)
        return conv_list

    async def get_hot_questions(self, quantity: int):
        questions = await asyncio.to_thread(
            self.hot_question_repo.get_hot_questions, quantity
        )
        
        return questions

    def add_hot_questions(self, questions: list):
        self.hot_question_repo.add_hot_questions(questions)


chat_dao = ChatDao()
