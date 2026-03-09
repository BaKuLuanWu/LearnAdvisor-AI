from sqlalchemy import Column,  DateTime
from datetime import datetime, timezone
from src.config.sql_db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid_extensions 

class BaseEntity(Base):
    """所有模型基类"""

    # 必须设置！让SQLAlchemy知道这是基类，不会创建对应的表
    __abstract__ = True


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid_extensions.uuid7, # uuid7后面不能加括号，否则会被当成函数调用只在类加载时触发一次，导致后续插入数据库时不调用函数而直接用初始调用值
        comment="主键ID(UUIDv7时间有序)"
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间"
    )