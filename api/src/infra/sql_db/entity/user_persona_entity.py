from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Text, JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from src.common.orm.base_entity import BaseEntity


class UserPersonaEntity(BaseEntity):
    """用户画像模型"""

    __tablename__ = "user_persona"
    __table_args__ = {
        "comment": "用户画像表"
    }

    basic_profile = Column(String, nullable=False, comment="用户信息")
    interests = Column(String, nullable=False, comment="兴趣点")
    dislikes = Column(String, nullable=False, comment="反感处")

    # 外键
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        comment="对话ID",
    )

    conversation = relationship(
        "ConversationEntity", back_populates="user_persona", lazy="noload"
    )

