from src.infra.sql_db.repo import (
    conv_repo,
    summary_repo,
    message_repo,
    user_persona_repo,
)
from src.model.schema.chat_schema import Summary
from src.infra.sql_db.entity.summary_entity import SummaryEntity


class ConvMemoryManageDao:

    def __init__(self):
        self.conv_repo = conv_repo
        self.message_repo = message_repo
        self.summary_repo = summary_repo
        self.user_persona_repo = user_persona_repo

    def get_chat_history(self, conv_id: str):
        conv = self.conv_repo.get_by_id(conv_id=conv_id)
        messages = conv.get("messages", []) if conv else []
        return messages

    def get_conv_ids(self):
        return self.conv_repo.get_conv_ids()

    def get_user_persona(self, conv_id: str):
        user_persona = self.conv_repo.get_user_persona(conv_id)
        if not user_persona:
            return None
        else:
            return {
                "user_role": user_persona.user_role,
                "major": user_persona.major,
                "grade": user_persona.grade,
                "learning_goal": user_persona.learning_goal,
                "current_courses": user_persona.current_courses,
                "knowledge_interests": user_persona.knowledge_interests,
                "question_types": user_persona.question_types,
                "file_analysis_preference": user_persona.file_analysis_preference,
                "reply_style_preference": user_persona.reply_style_preference,
                "knowledge_level": user_persona.knowledge_level,
                "topic_preferences": user_persona.topic_preferences,
                "dislikes": user_persona.dislikes,
            }

    def get_key_sentences(self, conv_id: str):
        key_sentences = None
        return key_sentences or ""

    def get_summaries(self, conv_id: str):
        summaries_text = ""
        summaries = self.conv_repo.get_summaries(conv_id)
        if summaries:
            for summary in summaries:
                if summary.start_index == summary.end_index:
                    summaries_text += f"\n对话{summary.start_index}:{summary.content}"
                else:
                    summaries_text += f"\n对话{summary.start_index}-{summary.end_index}:{summary.content}"
        print(f"摘要片段为:{summaries_text}")
        return summaries_text

    def get_max_turn(self, conv_id: str):
        return self.message_repo.get_max_turn(conv_id)

    def get_messages_by_range(self, conv_id: str, start_index: int, end_index: int):
        return self.message_repo.get_messages_by_range(conv_id, start_index, end_index)

    def get_recent_summary(self, conv_id: str):
        return self.summary_repo.get_recent_summary(conv_id)

    def add_summaries(self, summaries: list[Summary]):
        entity_list = [summary.to_entity() for summary in summaries]
        self.summary_repo.add_summaries(entity_list)

    def add_lv2_summaries(
        self, summaries: list[Summary], conv_id, start_index, end_index
    ):
        entity_list = [summary.to_entity() for summary in summaries]
        self.summary_repo.add_lv2_summaries(
            entity_list, conv_id, start_index, end_index
        )

    def get_recent_summary_level1_end_index(self, conv_id: str):
        return self.summary_repo.get_recent_summary_level1_end_index(conv_id)

    def get_recent_summary_level2_end_index(self, conv_id: str):
        return self.summary_repo.get_recent_summary_level2_end_index(conv_id)

    def get_summary_level2_count(self, conv_id: str):
        return self.summary_repo.get_summary_level2_count(conv_id)

    def get_summary_list_by_compress_times(self, conv_id: str, compress_times: int):
        entity_list = self.summary_repo.get_summary_list_by_compress_times(
            conv_id, compress_times
        )
        summaries = []
        for entity in entity_list:
            summary = Summary(
                entity.start_index,
                entity.end_index,
                entity.content,
                entity.conversation_id,
                entity.compress_times,
                entity.is_active,
            )
            summaries.append(summary)
        return summaries

    def update_user_persona(self, conv_id, user_persona, start_index, end_index):
        self.user_persona_repo.update_user_persona(conv_id, user_persona, start_index, end_index)


conv_memory_manage_dao = ConvMemoryManageDao()
