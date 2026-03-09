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
from src.config.sql_db import Base


class UploadFileChunkEntity(Base):
    """上传文件的切块模型"""

    __tablename__ = "upload_file_chunk"
    __table_args__ = {
        "comment": "上传文件分块表"
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    content = Column(Text, nullable=False)

    chunk_source = Column(String, nullable=False)

    parent_chunk_index = Column(Integer, nullable=False)

    child_chunk_index = Column(Integer, nullable=True)

    page_number = Column(Integer, nullable=True)

    page_name = Column(String, nullable=True)

    section = Column(String, nullable=True)

    # 外键
    upload_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("upload_file.id", ondelete="CASCADE"),
        nullable=False,
        comment="上传文件ID",
    )

    uploadfile = relationship(
        "UploadFileEntity", back_populates="uploadfile_chunks", lazy="noload"
    )
