from sqlalchemy import Column, String,  Boolean
from sqlalchemy.orm import relationship, validates
from src.common.orm.base_entity import BaseEntity

class UserEntity(BaseEntity):
    """用户模型"""
    __tablename__ = "user"
    __table_args__ = {
        "comment": "用户表"
    }

    username = Column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="用户名"
    )
    email = Column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="邮箱"
    )
    hashed_password = Column(
        String(255), 
        nullable=False,
        comment="哈希密码"
    )
   
    is_active = Column(
        Boolean, 
        default=True,
        comment="是否激活"
    )

    avatar_url = Column(
        String(500),
        nullable=True,
        comment="头像URL"
    )

    # 关系
    conversations = relationship("ConversationEntity", back_populates="user", cascade="all, delete-orphan",lazy="noload")
    
    # 验证器
    @validates('email')
    def validate_email(self, key, email):
        """验证邮箱格式"""
        if '@' not in email:
            raise ValueError("无效的邮箱地址")
        return email.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        """验证用户名"""
        if len(username) < 2:
            raise ValueError("用户名至少2个字符")
        return username
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

