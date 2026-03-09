from sqlalchemy import Column
from sqlalchemy.orm import relationship, validates
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    ForeignKey,
    Index,
)

from sqlalchemy.dialects.postgresql import UUID
from src.common.orm.base_entity import BaseEntity


class ConversationEntity(BaseEntity):
    """对话模型"""

    __tablename__ = "conversation"
    __table_args__ = {"comment": "对话记录表"}

    # 对话基本信息
    title = Column(String(200), nullable=True, comment="对话标题")

    # 外键：关联用户
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),  # 级联删除
        nullable=False,
        index=True,
        comment="所属用户ID",
    )

    user = relationship("UserEntity", back_populates="conversations")
    messages = relationship(
        "MessageEntity",
        back_populates="conversation",
        cascade="all, delete-orphan",  # 删除对话时级联删除消息
        order_by="MessageEntity.created_at.asc()",  # 按时间排序
        lazy="select",
    )
    summaries = relationship(
        "SummaryEntity",
        back_populates="conversation",
        cascade="all, delete-orphan",  # 删除对话时级联删除消息
        order_by="SummaryEntity.created_at.asc()",  # 按时间排序
        lazy="select",
    )
    user_persona = relationship(
        "UserPersonaEntity",
        back_populates="conversation",
        cascade="all, delete-orphan",  # 删除对话时级联删除消息
        lazy="select",
    )

    # 对话状态
    is_active = Column(Boolean, default=True, comment="是否活跃对话")

    # 统计信息
    message_count = Column(Integer, default=0, comment="消息总数")

    last_message_at = Column(
        DateTime(timezone=True), nullable=True, comment="最后消息时间"
    )

    # 复合索引：经常按用户和时间查询
    __table_args__ = (Index("idx_user_created", "user_id", "created_at"),)
