from typing import Dict
from src.service.intent_service import intent_service
from src.config.static.subject import SUBJECT_LIST


# ========== 意图识别模块 ==========
class IntentRecognizer:
    """意图识别器（支持基于规则/模型）"""

    def __init__(self):

        self.external_service = intent_service

        # 槽位提取规则
        self.slot_patterns = {
            "course": ["课程", "课", "教学", "学"],
            # 不需要多步骤
            "profession": [
                "行业",
                "市场",
                "前景",
                "发展",
                "领域",
                "方面",
                "学习路线",
                "学习规划",
                "学习建议",
                "工作",
                "就业",
                "薪资",
                "职业发展",
                "岗位",
            ],
        }

    def recognize(self, user_input: str, intent_history: str) -> Dict:
        """识别意图和槽位"""

        result = self.external_service.process(user_input, intent_history)

        # 槽位提取
        slots = self._extract_slots(user_input)

        return {
            "intent": result.intent,
            "slots": slots,
            "confidence": result.confidence,
        }

    def _extract_slots(self, text: str) -> Dict:
        # 要统一小写
        text_lower = text.lower()
        titles_lower = [title.lower() for title in SUBJECT_LIST]
        slots = {}

        # 课程类获取
        for kw in self.slot_patterns["course"]:
            kw_pos = text_lower.find(kw)
            if kw_pos != -1:
                for title in titles_lower:
                    title_pos = text_lower.find(title)
                    if title_pos != -1:
                        if kw_pos - title_pos - len(title) == 1:
                            print(f"在左边匹配到课程: {title}")
                            slots["course"] = title
                            break
                        elif kw == "学" and title_pos - kw_pos in [1, 2]:
                            slots["course"] = title
                            print(f"在右边匹配到课程: {title}")
                            break
        # 专业类获取
        for kw in self.slot_patterns["profession"]:
            kw_pos = text_lower.find(kw)
            if kw_pos != -1:
                for title in titles_lower:
                    title_pos = text_lower.find(title)
                    if title_pos != -1:
                        if kw_pos - title_pos - len(title) == 1:
                            print(f"在左边匹配到专业: {title}")
                            slots["profession"] = title
                            break
        return slots
