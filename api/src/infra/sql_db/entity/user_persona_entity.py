from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from src.common.orm.base_entity import BaseEntity


class UserPersonaEntity(BaseEntity):
    """用户画像模型"""

    __tablename__ = "user_persona"
    __table_args__ = {"comment": "用户画像表"}

    # 基础信息
    user_role = Column(String(20), nullable=True, comment="用户角色: student/teacher/professional/visitor")
    major = Column(String(100), nullable=True, comment="专业/领域")
    grade = Column(String(20), nullable=True, comment="年级/学段: freshman/sophomore/junior/senior/graduate/other")
    
    # 数组字段 - 使用 PostgreSQL 原生 ARRAY 类型
    learning_goal = Column(ARRAY(String(50)), nullable=True, comment="学习目标: 考研/就业/考证书/兴趣拓展/其他")
    current_courses = Column(ARRAY(String(200)), nullable=True, comment="当前学习课程")
    knowledge_interests = Column(ARRAY(String(100)), nullable=True, comment="关注的知识领域")
    question_types = Column(ARRAY(String(50)), nullable=True, comment="常见问题类型: 课程查询/概念解释/作业辅导/职业规划")
    topic_preferences = Column(ARRAY(String(100)), nullable=True, comment="话题偏好")
    
    # 枚举字段
    file_analysis_preference = Column(String(20), nullable=True, comment="文件解析偏好: summary/deep/comparative")
    reply_style_preference = Column(String(20), nullable=True, comment="回复风格: concise/detailed/encouraging/professional")
    
    # 复杂对象
    knowledge_level = Column(JSONB, nullable=True, comment="知识掌握程度: (领域: beginner/intermediate/advanced)")
    
    # 其他
    dislikes = Column(ARRAY(String(200)), nullable=True, comment="反感点")

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
