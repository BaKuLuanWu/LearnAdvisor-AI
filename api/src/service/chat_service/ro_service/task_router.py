from .dialog_state import DialogState
from typing import Dict
from .intent_recognizer import IntentRecognizer
from .context_query_engine import context_query_engine
from .title_match import title_match


# ========== 任务路由决策器 ==========
class TaskRouter:
    """任务路由器"""

    def __init__(self):
        # 定义每个意图所需的槽位
        self.intent_requirements = {
            "course_query_and_answer": ["course"],
            "professional_consulting": ["profession"],
        }

        # 定义下一步动作
        self.action_handlers = {
            "ask_clarification": self._handle_ask_clarification,
            "collect_slots": self._handle_collect_slots,
            "execute_task": self._handle_execute_task,
            "switch_task": self._handle_switch_task,
        }

    def decide_next_action(self, state: DialogState, intent_history: str) -> Dict:
        """
        决定下一步动作
        返回：{"action": "action_name", "params": {...}, "response": "回复文本"}
        """

        # 用户要返回上一个话题（后续根据状态机的映射表判断当前话题以及"上上个"这种需要栈解决的）
        if context_query_engine.is_query(state.user_input):
            return self._decide_based_on_state(state)

        # 用户意图不清晰，例如“我想问金融”，无法确定是课程问答/专业咨询
        title_match_result =title_match.process(state.user_input)
        if title_match_result:
            if state.intent not in [
                "course_query_and_answer",
                "professional_consulting",
            ]:
                state.update_slot('course', title_match_result)
                state.update_slot('profession', title_match_result)
                return self._handle_collect_slots(state, None)
            else:
                new_slots = IntentRecognizer()._extract_slots(state.user_input)
                for slot_name, value in new_slots.items():
                    state.update_slot(slot_name, value)
                return self._decide_based_on_state(state)

        new_intent_result = IntentRecognizer().recognize(
            state.user_input, intent_history
        )
        new_intent = new_intent_result["intent"]
        new_slots = new_intent_result["slots"]

        if new_intent == "unknown":
            return self.action_handlers["ask_clarification"](
                "抱歉，这个问题我无法回答。", "unknown"
            )

        # 新对话
        elif state.intent is None:
            state.intent = new_intent
            # 设置必需槽位
            state.required_slots = self.intent_requirements.get(state.intent, [])
            # 提取槽位
            for slot_name, value in new_slots.items():
                state.update_slot(slot_name, value)

            return self._decide_based_on_state(state)

        # 意图变化
        elif state.intent != new_intent or any(
            kw in state.user_input
            for kw in ["等一下", "先别管", "换个", "另外", "对了"]
        ):
            self.action_handlers["switch_task"](state, new_intent)
            for slot_name, value in new_slots.items():
                state.update_slot(slot_name, value)

            return self._decide_based_on_state(state)

        # 意图不变
        else:
            for slot_name, value in new_slots.items():
                state.update_slot(slot_name, value)
            return self._decide_based_on_state(state)

    def _decide_based_on_state(self, state: DialogState) -> Dict:
        """基于当前状态决策"""
        missing_slots = state.get_missing_slots()

        if missing_slots:
            # 还有缺失槽位，继续收集，比如课程、行业前面缺少专业名词
            print("还有缺失槽位，继续收集")
            next_slot = missing_slots[0]
            return self.action_handlers["collect_slots"](state, next_slot)

        else:
            # 所有槽位已收集，执行任务
            print("所有槽位已收集，执行任务")
            return self.action_handlers["execute_task"](state)

    # ========== 动作处理器 ==========

    def _handle_ask_clarification(self, message: str, intent: str) -> Dict:
        """处理请求澄清"""
        return {
            "action": "ask_clarification",
            "response": message,
            "params": {"intent": intent},
        }

    def _handle_collect_slots(self, state: DialogState, slot_name: str) -> Dict:
        """处理收集槽位"""
        slot_questions = {
            "course": "请问您想问的是哪一门课程？",
            "profession": "请问您想了解的是哪一个行业？",
        }

        if not slot_name:
            return {
                "action": "collect_slots",
                "response": "请问你想问的是关于它的课程信息还是行业咨询？",
                "params": {"slot_name": slot_name, "intent": state.intent},
            }

        question = slot_questions.get(slot_name, f"请提供{slot_name}的相关信息。")
        return {
            "action": "collect_slots",
            "response": question,
            "params": {"slot_name": slot_name, "intent": state.intent},
        }

    def _handle_execute_task(self, state: DialogState) -> Dict:
        """处理执行任务"""
        return {
            "action": "execute_task",
            "response": "执行回复模块",
            "params": {"intent": state.intent},
        }

    def _handle_switch_task(self, state: DialogState, new_intent: str) -> Dict:
        """处理任务切换"""

        # 在映射表中查看相同任务
        flag = False
        for key, value in state.task_map.items():
            if value.get("intent") == state.intent:
                flag = True
                value["slots"] = state.slots
                value["required_slots"] = state.required_slots
                # 在栈中定位
                if state.task_stack:
                    while state.task_stack:
                        task_id = state.task_stack.pop()
                        if key == task_id:
                            break
                state.task_stack.append(key)
                break
        if not flag:
            task_id = f"task_00{len(state.task_map)}"
            state.task_map[task_id] = {
                "intent": state.intent,
                "slots": state.slots,
                "required_slots": state.required_slots,
            }
            state.task_stack.append(task_id)


task_router = TaskRouter()
