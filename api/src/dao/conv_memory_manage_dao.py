from src.infra.sql_db.repo import conv_repo, summary_repo, message_repo
from src.model.schema.chat_schema import Summary
from src.infra.sql_db.entity.summary_entity import SummaryEntity


class ConvMemoryManageDao:

    def __init__(self):
        self.conv_repo = conv_repo
        self.message_repo = message_repo
        self.summary_repo = summary_repo

    def get_chat_history(self, conv_id: str):
        conv = self.conv_repo.get_by_id(conv_id=conv_id)
        messages = conv.get("messages", []) if conv else []
        return messages

    def get_conv_ids(self):
        return self.conv_repo.get_conv_ids()

    def get_user_persona(self, conv_id: str):
        user_persona = self.conv_repo.get_user_persona(conv_id)
        if user_persona == None:
            return "\n兴趣偏好：该用户对投资很感兴趣"

        if user_persona.basic_profile:
            user_persona_text += f"\n个人信息：{user_persona.basic_profile}"
        if user_persona.interests:
            user_persona_text += f"\n兴趣偏好：{user_persona.interests}"
        if user_persona.dislikes:
            user_persona_text += f"\n反感点：{user_persona.dislikes}"

        return user_persona_text

    def get_key_sentences(self, conv_id: str):
        key_sentences = (
            "1.2008年金融危机对全球产生广泛影响。\n2.近几年中国GDP稳步增长。"
        )
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

    def get_summary_level1_list(self, conv_id: str):
        entity_list = self.summary_repo.get_summary_level1_list(conv_id)
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


conv_memory_manage_dao = ConvMemoryManageDao()
