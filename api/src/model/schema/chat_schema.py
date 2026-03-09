from dataclasses import dataclass
from typing import Text
from src.infra.sql_db.entity.summary_entity import SummaryEntity


@dataclass
class ChatMessage:
    role: str
    content: str
    intent: str
    recommend: bool


@dataclass
class Summary:
    start_index: int
    end_index: int
    content: Text
    conv_id: str
    compress_times: int
    is_active: bool

    def to_entity(self):
        return SummaryEntity(
            conversation_id=self.conv_id,
            start_index=self.start_index,
            end_index=self.end_index,
            content=self.content,
            compress_times=self.compress_times,
            is_active=True,
        )
