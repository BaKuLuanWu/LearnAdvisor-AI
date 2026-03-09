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
    BigInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from src.common.orm.base_entity import BaseEntity


class HotQuestionEntity(BaseEntity):
    """热门问题模型"""

    __tablename__ = "hot_question"
    __table_args__ = {"comment": "热门问题表"}

    content = Column(Text, nullable=False)
    
    click_times = Column(BigInteger,nullable=False)