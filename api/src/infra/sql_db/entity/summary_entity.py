from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from src.config.sql_db import Base


class SummaryEntity(Base):
    """对话摘要模型"""

    __tablename__ = "summary"
    __table_args__ = {"comment": "摘要表"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    start_index = Column(Integer, nullable=False, comment="起始轮次")
    end_index = Column(Integer, nullable=False, comment="结束轮次")

    content = Column(Text, nullable=False, comment="摘要内容")

    # 外键
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        comment="对话ID",
    )

    conversation = relationship(
        "ConversationEntity", back_populates="summaries", lazy="noload"
    )

    compress_times = Column(
        Integer, nullable=False, default=0, comment="压缩次数"
    )  # 若超过两次则直接更新用户画像

    is_active = Column(
        Boolean, nullable=False, default=True, comment="是否活跃，false表示过期"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )
