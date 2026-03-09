from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey,BigInteger
from sqlalchemy.orm import relationship
from src.common.orm.base_entity import BaseEntity

class UploadFileEntity(BaseEntity):
    """上传文件模型"""
    __tablename__ = "upload_file"
    __table_args__ = {
        "comment": "上传文件表"
    }

    file_path = Column(String,nullable=False)

    file_name= Column(String,nullable=False)

    file_size= Column(BigInteger,nullable=False)

    file_hash= Column(String,nullable=False)

    file_type= Column(String,nullable=False)

    page_count= Column(Integer,nullable=True)

    author= Column(String,nullable=True)

    title= Column(String,nullable=True)

    word_count= Column(Integer,nullable=True)

    character_count= Column(Integer,nullable=True)
    
    uploadfile_chunks = relationship(
        "UploadFileChunkEntity",
        back_populates="uploadfile",
        cascade="all, delete-orphan",  # 删除对话时级联删除消息
        lazy="select"
    )
    
    