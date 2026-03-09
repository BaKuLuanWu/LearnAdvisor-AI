from ..entity.conversation_entity import ConversationEntity
from ..entity.user_persona_entity import UserPersonaEntity
from ..entity.summary_entity import SummaryEntity
from src.model.schema.chat_schema import Summary
from datetime import datetime
from src.config import db_manager
from src.config.settings import setup_logging

logger = setup_logging()


class ConversationRepository:

    def __init__(self):
        pass

    def get_conversation_list(self, user_id: str):
        """根据用户id获取对话列表"""
        with db_manager.session_scope() as session:
            conv_list = session.query(ConversationEntity).filter(
                ConversationEntity.user_id == user_id
            )
            print()
            conv_list_response = []
            if conv_list:
                for conv in conv_list:
                    print(
                        {
                            "conv_id": str(conv.id),
                            "title": conv.title,
                            "created_at": str(conv.created_at),
                        }
                    )
                    conv_list_response.append(
                        {
                            "conv_id": str(conv.id),
                            "title": conv.title,
                            "created_at": str(conv.created_at),
                        }
                    )
                return conv_list_response
            return None

    def get_by_id(self, conv_id: str):
        """根据对话id获取对话详情"""
        with db_manager.session_scope() as session:
            conv = (
                session.query(ConversationEntity)
                .filter(ConversationEntity.id == conv_id)
                .first()
            )

            return (
                {"conv_id": conv.id, "title": conv.title, "messages": conv.messages}
                if conv
                else None
            )

    def create_conversation(self, title, user_id):
        with db_manager.session_scope() as session:
            conv = ConversationEntity(title=title, user_id=user_id)
            session.add(conv)
            session.flush()
            print(f"对话创建成功: {conv.title} (ID: {conv.id})")

            return conv.id

    def add_user_persona(self, conv_id: str, desc: dict):
        with db_manager.session_scope() as session:
            user_persona = UserPersonaEntity(
                basic_profile=desc["basic_profile"],
                interests=desc["interests"],
                dislikes=desc["dislikes"],
                conv_id=conv_id,
            )
            session.add(user_persona)

    def get_user_persona(self, conv_id: str):
        with db_manager.session_scope() as session:
            user_persona = (
                session.query(UserPersonaEntity)
                .filter(UserPersonaEntity.conversation_id == conv_id)
                .first()
            )

            return user_persona

    def add_summaries(self, summaries: list[Summary]):
        entity_list = []
        for summary in summaries:
            entity_list.append(summary.to_entity())
        with db_manager.session_scope() as session:
            session.add_all(entity_list)

    def get_summaries(self, conv_id: str):
        with db_manager.session_scope() as session:
            entity_list = (
                session.query(SummaryEntity)
                .filter(
                    SummaryEntity.conversation_id == conv_id,
                    SummaryEntity.is_active == True,
                )
                .order_by(SummaryEntity.start_index)
                .all()
            )

            return entity_list

    # 新增消息时更新当前对话部分字段
    def update_conversation(self, conv_id: str):
        with db_manager.session_scope() as session:
            entity = (
                session.query(ConversationEntity)
                .filter(ConversationEntity.id == conv_id)
                .first()
            )
            if entity:
                entity.message_count += 2
                entity.last_message_at = datetime.now()
                logger.info("对话记录更新成功")
            else:
                logger.error("更新出错，对话不存在")

    def get_conv_ids(self):
        with db_manager.session_scope() as session:
            id_tuples = session.query(ConversationEntity.id).all()
            return [id_tuple[0] for id_tuple in id_tuples]  # 转换为纯id列表


conv_repo = ConversationRepository()
