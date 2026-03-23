"""对话管理服务，负责将聊天产生的信息拆分成用户画像、关键语句向量、摘要、工作记忆"""

from .schedule_task import schedule_task
from src.dao import conv_memory_manage_dao
import json


class ConvMemoryManageService:

    def __init__(self):
        self.conv_memory_manage_dao = conv_memory_manage_dao
        self.schedule = schedule_task

    # 返回工作记忆或工作记忆+额外上下文(用户画像+关键语句+摘要)
    def get_chat_history_context(self, conv_id: str, priority: str) -> tuple[list, str]:

        chat_history = self.conv_memory_manage_dao.get_chat_history(conv_id)
        if priority == "medium":
            return chat_history[-40:], ""

        extra_context = "###额外上下文"
        user_persona = self.conv_memory_manage_dao.get_user_persona(conv_id)
        if user_persona:
            user_persona_json = json.dumps(user_persona, ensure_ascii=False, indent=2)
            extra_context += f"\n用户画像:{user_persona_json}"

        key_sentences = self.conv_memory_manage_dao.get_key_sentences(conv_id)
        if key_sentences:
            extra_context += f"\n关键语句:{key_sentences}"

        summaries = self.conv_memory_manage_dao.get_summaries(conv_id)
        if summaries:
            extra_context += f"\n历史对话片段摘要:{summaries}"

        return chat_history[-40:], extra_context


conv_memory_manage_service = ConvMemoryManageService()
