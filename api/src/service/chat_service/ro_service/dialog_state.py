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

    def to_dict(self) -> dict:
        """将 DialogState 对象转换为字典"""
        return {
            "conv_id": self.conv_id,
            "user_input": self.user_input,
            "intent": self.intent,
            "slots": self.slots,
            "required_slots": self.required_slots,
            "history": self.history,
            "task_stack": self.task_stack,
            "task_map": self.task_map,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DialogState':
        """从字典恢复 DialogState 对象"""
        state = cls(conv_id=data["conv_id"])
        state.user_input = data.get("user_input", "")
        state.intent = data.get("intent")
        state.slots = data.get("slots", {})
        state.required_slots = data.get("required_slots", [])
        state.history = data.get("history", [])
        state.task_stack = data.get("task_stack", [])
        state.task_map = data.get("task_map", {})
        
        # 处理时间字段
        if data.get("created_at"):
            state.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_updated"):
            state.last_updated = datetime.fromisoformat(data["last_updated"])
        
        return state
