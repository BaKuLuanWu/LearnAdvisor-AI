from typing import Optional, Dict, Any, List
from datetime import datetime


class DialogState:
    """对话状态机"""

    def __init__(self, conv_id: str):
        self.conv_id = conv_id
        self.user_input = ""
        self.intent: Optional[str] = None  # 当前正在执行中的任务意图，unknown不计算在内
        self.slots: Dict[str, Any] = {}
        self.required_slots: List[str] = []  # 当前意图所需的槽位
        self.history: List[Dict] = []  # 对话历史
        self.task_stack: List[str] = []  # 任务栈（支持任务中断/恢复）
        self.task_map: Dict = (
            {}
        )  # 任务映射表(如{"task_001":{"intent":"course_query","slots": {"name": "金融"},"missing_slots": []}})
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

    def add_history(self, role: str, content: str):
        """记录对话历史"""
        self.history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

    def update_slot(self, slot_name: str, value: Any):
        """更新槽位值"""
        self.slots[slot_name] = value
        self.last_updated = datetime.now()

    def get_missing_slots(self) -> List[str]:
        """获取缺失的必要槽位"""
        return [slot for slot in self.required_slots if slot not in self.slots]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "conv_id": self.conv_id,
            "current_intent": (self.current_intent if self.current_intent else None),
            "slots": self.slots,
            "missing_slots": self.get_missing_slots(),
            "history_length": len(self.history),
        }
