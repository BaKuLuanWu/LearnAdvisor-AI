from ..entity.conversation_entity import ConversationEntity
from ..entity.message_entity import MessageEntity
from src.model.schema.chat_schema import ChatMessage
from src.config import db_manager
from sqlalchemy.sql import func


class MessageRepository:

    def __init__(self):
        pass

    def get_message_list(self, conv_id: str):
        """根据对话id获取消息列表"""
        with db_manager.session_scope() as session:
            return session.query(MessageEntity).filter(
                MessageEntity.conversation_id == conv_id
            )

    def get_latest_message(self, conv_id: str):
        """获取最新消息"""
        with db_manager.session_scope() as session:
            return (
                session.query(ConversationEntity)
                .filter(ConversationEntity.id == conv_id)
                .first()
            )

    def add_message(self, conv_id, msg: ChatMessage):
        with db_manager.session_scope() as session:

            max_seq_query = session.query(func.max(MessageEntity.sequence)).filter(
                MessageEntity.conversation_id == conv_id
            )
            current_seq_max = max_seq_query.scalar() or 0

            max_turn_query = session.query(
                func.max(MessageEntity.turn).filter(
                    MessageEntity.conversation_id == conv_id,
                    MessageEntity.role == msg.role,
                )
            )
            current_turn_max = max_turn_query.scalar() or 0
            message = MessageEntity(
                conversation_id=conv_id,
                content=msg.content,
                role=msg.role,
                sequence=current_seq_max + 1,
                turn=current_turn_max + 1,
                intent=msg.intent,
                recommend=msg.recommend,
            )
            session.add(message)
            session.flush()

    def get_max_turn(self, conv_id: str):
        with db_manager.session_scope() as session:
            return (
                session.query(func.max(MessageEntity.turn))
                .filter(MessageEntity.conversation_id == conv_id)
                .scalar()
            )

    def get_messages_by_range(self, conv_id: str, start_index: int, end_index: int):
        with db_manager.session_scope() as session:
            return (
                session.query(MessageEntity)
                .filter(
                    MessageEntity.conversation_id == conv_id,
                    MessageEntity.turn.between(start_index, end_index),
                )
                .order_by(MessageEntity.turn.asc(), MessageEntity.sequence.asc())
                .all()
            )


message_repo = MessageRepository()
