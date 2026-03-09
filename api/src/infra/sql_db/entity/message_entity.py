from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from src.common.orm.base_entity import BaseEntity


class MessageEntity(BaseEntity):
    """历史对话模型"""

    __tablename__ = "message"
    __table_args__ = {"comment": "对话消息表"}

    content = Column(Text, nullable=False)
    role = Column(String(20), default="user")

    # 外键
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        comment="对话ID",
    )

    conversation = relationship(
        "ConversationEntity", back_populates="messages", lazy="noload"
    )

    # 消息序号（对话内排序）
    sequence = Column(Integer, nullable=False, comment="消息序号")

    # 对话内轮数
    turn = Column(Integer, nullable=False, comment="对话轮数")

    intent = Column(String(50), nullable=True, comment="消息意图")

    recommend = Column(Boolean,nullable=True,comment='是否推荐问题过')


'''
from sqlalchemy.orm import Session
import threading

# 线程本地缓存（减少数据库查询）
_local_cache = threading.local()

def get_local_cache():
    if not hasattr(_local_cache, 'sequence_map'):
        _local_cache.sequence_map = {}
    return _local_cache.sequence_map

@event.listens_for(Session, 'after_commit')
def clear_cache(session):
    """提交后清空缓存"""
    if hasattr(_local_cache, 'sequence_map'):
        _local_cache.sequence_map.clear()

@event.listens_for(Message, 'before_insert')
def set_message_sequence_cached(mapper, connection, target):
    """带缓存的sequence设置"""
    if target.conversation_id and target.sequence is None:
        conv_key = str(target.conversation_id)
        cache = get_local_cache()
        
        # 检查缓存
        if conv_key in cache:
            cache[conv_key] += 1
            target.sequence = cache[conv_key]
        else:
            # 查询数据库
            lock_key = hash(conv_key) % (2**31)
            lock_stmt = text("SELECT pg_advisory_xact_lock(:lock_key)")
            connection.execute(lock_stmt, {"lock_key": lock_key})
            
            query_stmt = text("""
                SELECT COALESCE(MAX(sequence), 0) 
                FROM messages 
                WHERE conversation_id = :conv_id::uuid
            """)
            result = connection.execute(
                query_stmt, 
                {"conv_id": conv_key}
            )
            current_max = result.scalar() or 0
            
            # 设置并缓存
            target.sequence = current_max + 1
            cache[conv_key] = target.sequence
'''
