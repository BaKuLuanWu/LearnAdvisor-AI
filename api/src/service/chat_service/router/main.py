from typing import Dict
from src.service.upload_file_service import UploadFileService
from src.model.dto.request import ChatQueryDTO
from src.model.schema.chat_schema import ChatMessage
from src.dao import chat_dao
from .pre_search import pre_search
from .intent_recognizer import IntentRecognizer
from ..query_recommend import query_recommend
from .reply_module import ReplyModule
from .dialog_state import DialogState
from .context_query_engine import context_query_engine
from src.config import setup_logging

logger = setup_logging()


INTENT_MAPPING = {
    "course_query_and_answer": "课程信息",
    "professional_consulting": "行业前景、就业咨询、学习规划",
    "file_content_query": "文档分析",
    "daily_chat": "日常生活",
}


def save_conv_turn(
    conv_id: str, user_input: str, answer: str, intent: str, recommend: bool
):
    new_conv_round = [
        ChatMessage("user", user_input, intent, None),
        ChatMessage("assistant", answer, None, recommend),
    ]
    chat_dao.save_round_of_conv(conv_id, new_conv_round)


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
            "execute_task": self._handle_execute_task,  # 只有这一步才调用回复大模型
            "switch_task": self._handle_switch_task,
        }

    # 意图识别记录是最近五轮
    def decide_next_action(
        self,
        state: DialogState,
        user_input: str,
        intent_history: str,
        exist_files: bool,
    ) -> Dict:
        """
        决定下一步动作
        返回：{"action": "action_name", "params": {...}, "response": "回复文本"}
        """

        if exist_files:
            intent = "file_content_query"
            slots = {}
        # 判断用户是否想要紧接上文，例如:"刚刚我问了什么？"
        elif context_query_engine.is_query(user_input):
            print("上下文检查引擎被调用")
            intent = state.current_intent
            slots = state.slots
        # 前置查询(只提了专业名词，没有带课程、行业等后缀)
        elif pre_search.process(user_input):
            pre_search_result = pre_search.process(user_input)
            intent = "unknown"
            slots = {"course": pre_search_result, "profession": pre_search_result}
            for slot_name, value in slots.items():
                    state.update_slot(slot_name, value)
            print(f"前置查询处结果:{pre_search_result}")
            return self.action_handlers["ask_clarification"](
                    state, pre_search_result, "unknown"
            )
        else:
            intent_result = IntentRecognizer().recognize(user_input, intent_history)
            intent = intent_result["intent"]
            print(f"意图识别结果:{intent}")
            slots = intent_result["slots"]
            print(slots)

        if intent == "unknown":
            # 保持上下文关联
            if (
                state.current_intent
                in [
                    "daily_chat",
                    "course_query_and_answer",
                    "professional_consulting",
                    "file_content_query",
                ]
                and state.fuzzy_decision < 4
            ):
                print("保持上下文关联")
                print(f"当前历史意图:{state.current_intent}")
                state.fuzzy_decision += 1
                print(f"困惑次数:{state.fuzzy_decision}")
                # 提取槽位
                for slot_name, value in slots.items():
                    state.update_slot(slot_name, value)
                return self._decide_based_on_state(state)
            else:
                return self.action_handlers["ask_clarification"](
                    state, "抱歉，这个问题我无法回答。", "unknown"
                )

        # 新对话
        elif state.current_intent is None:

            state.current_intent = intent
            # 设置必需槽位
            state.required_slots = self.intent_requirements.get(
                state.current_intent, []
            )
            # 提取槽位
            for slot_name, value in slots.items():
                state.update_slot(slot_name, value)

            return self._decide_based_on_state(state)

        # 意图变化时
        elif intent != state.current_intent or any(
            kw in user_input for kw in ["等一下", "先别管", "换个", "另外", "对了"]
        ):
            self.action_handlers["switch_task"](state, intent)
            state.fuzzy_decision = 0
            # 合并提取的槽位
            for slot_name, value in slots.items():
                state.update_slot(slot_name, value)

            return self._decide_based_on_state(state)

        # 正常执行
        else:
            print("正常执行")
            state.fuzzy_decision = 0
            for slot_name, value in slots.items():
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

    def _handle_ask_clarification(
        self, state: DialogState, message: str, intent: str
    ) -> Dict:
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

        question = slot_questions.get(slot_name, f"请问{slot_name}是什么？")
        return {
            "action": "collect_slots",
            "response": question,
            "params": {"slot_name": slot_name, "intent": state.current_intent},
        }

    def _handle_execute_task(self, state: DialogState) -> Dict:
        """处理执行任务"""
        return {
            "action": "execute_task",
            "response": "执行回复模块",
            "params": {"intent": state.current_intent},
        }

    def _handle_switch_task(self, state: DialogState, new_intent: str) -> Dict:
        """处理任务切换"""

        print(f"当前行为是任务切换")

        # 可能用户说了想换个话题，但是实际上讲的还是原来的，要再次确认下
        if new_intent == state.current_intent:
            response = f"抱歉，没能理解您的问题。您是想聊{INTENT_MAPPING.get(new_intent,'日常生活')}方面的吗？"

            return self.action_handlers["ask_clarification"](
                state, response, new_intent
            )

        # 保存当前任务到栈中
        elif state.task_stack and state.task_stack[0].get("intent") == new_intent:
            # A-B-A
            task = state.task_stack.pop()
            state.current_intent = task.get("intent")
            state.required_slots = task.get("required_slots")
            state.slots = task.get("slots")

        else:  # 栈为空 or A-B-C
            if state.task_stack:
                state.task_stack.pop()

            state.task_stack.append(
                {
                    "intent": state.current_intent,
                    "slots": state.slots.copy(),
                    "required_slots": state.required_slots.copy(),
                }
            )

            state.current_intent = new_intent
            state.required_slots = self.intent_requirements.get(new_intent, [])
            state.slots = {}  # 重置槽位


class DialogueManager:
    """对话管理器"""

    def __init__(self):
        self.conversations: Dict[str, DialogState] = {}
        self.recognizer = IntentRecognizer()
        self.router = TaskRouter()
        self.reply_module = ReplyModule()

    async def process(
        self, dto: ChatQueryDTO, chat_history: list, extra_context: str
    ) -> Dict:
        """处理用户输入"""
        conv_id = dto.conv_id
        user_input = dto.user_input

        exist_files = False
        if dto.files:
            """将新文件加入向量数据库中"""
            exist_files = True
            upload_file_service = UploadFileService(conv_id)
            upload_file_service.process_files(dto.files)

        # 获取或创建对话状态
        if conv_id not in self.conversations:
            self.conversations[conv_id] = DialogState(conv_id)

        state = self.conversations[conv_id]
        state.user_input = user_input
        intent_history = self._get_intent_history(chat_history[-10:])
        print(f"意图识别历史结果:{intent_history}")

        # 路由决策
        action_result = self.router.decide_next_action(
            state, user_input, intent_history, exist_files
        )

        if action_result["action"] == "execute_task":
            print("执行节点")
            response = self.reply_module.process(
                conv_id,
                user_input,
                action_result["params"].get("intent", ""),
                chat_history[-10:],
                extra_context,
            )
            query_recommend_content = await query_recommend.process(
                user_input, chat_history, state.current_intent
            )
            if query_recommend_content:
                response += f"\n\n{query_recommend_content}"
                save_conv_turn(
                    conv_id, user_input, response, state.current_intent, True
                )
            else:
                save_conv_turn(
                    conv_id, user_input, response, state.current_intent, False
                )

            return response

        # 意图信息补充不使用问题推荐
        elif action_result["action"] == "collect_slots":
            logger.info(f"最终节点为:collect_slots")
            response = action_result["response"]
            save_conv_turn(
                conv_id,
                user_input,
                response,
                action_result["params"].get("intent", ""),
                False,
            )
            return response

        else:
            logger.info(f'未执行回复模块,当前行为是:{action_result["action"]}')
            response = action_result["response"]

            query_recommend_content = await query_recommend.process(
                user_input, chat_history, action_result["params"].get("intent", "")
            )
            if query_recommend_content:
                response += f"\n\n{query_recommend_content}"
                save_conv_turn(
                    conv_id,
                    user_input,
                    response,
                    action_result["params"].get("intent", ""),
                    True,
                )
            else:
                save_conv_turn(
                    conv_id,
                    user_input,
                    response,
                    action_result["params"].get("intent", ""),
                    False,
                )

            return response

    # 只检索近5轮对话的意图
    def _get_intent_history(self, chat_history: list) -> str:
        if not chat_history:
            print("历史记录为空")
            return "无"

        import json

        intent_history = []
        for i, msg in enumerate(chat_history):
            if msg.role == "user":
                if i == len(chat_history) - 2:
                    obj = {
                        "user_input": msg.content,
                        "ai_response": chat_history[i + 1].content[-100:],
                        "intent": msg.intent,
                    }
                    intent_history.append(obj)
                    break
                else:
                    obj = {"user_input": msg.content, "intent": msg.intent}
                    intent_history.append(obj)

        intent_history_json = json.dumps(intent_history, ensure_ascii=False)
        print(intent_history_json)
        return intent_history_json


dialogue_manager = DialogueManager()
