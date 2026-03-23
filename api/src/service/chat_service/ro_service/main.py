from typing import Dict
from src.service.upload_file_service import UploadFileService
from src.model.dto.request import ChatQueryDTO
from .task_router import task_router
from src.dao import chat_dao
from ..query_recommend import query_recommend
from .reply_module import ReplyModule
from .dialog_state import DialogState
import json
import asyncio
from src.config import setup_logging

logger = setup_logging()


class DialogueManager:
    """对话管理器"""

    def __init__(self):
        self.conversations: Dict[str, DialogState] = {}
        self.chat_dao = chat_dao
        self.task_router = task_router
        self.reply_module = ReplyModule()

    async def process(self, dto: ChatQueryDTO, chat_history: list, extra_context: str):
        """处理用户输入"""
        conv_id = dto.conv_id
        user_input = dto.user_input

        # 解析文件
        if dto.files:
            upload_file_service = UploadFileService(conv_id)
            upload_file_service.process_files(dto.files)

        # 获取或创建对话状态
        state = self.chat_dao.get_dialog_state(conv_id)
        print(f"状态机的值:{state.to_dict()}")

        state.user_input = user_input
        intent_history = self._get_intent_history(chat_history[-10:])
        print(f"意图识别历史结果:{intent_history}")

        # 路由决策
        action_result = self.task_router.decide_next_action(state, intent_history)

        ai_response = ""
        intent = ""
        recommend = False
        if action_result["action"] == "execute_task":
            intent = state.intent
            buffer = ""
            async for chunk in self.reply_module.process(
                conv_id,
                user_input,
                action_result["params"].get("intent", ""),
                action_result["params"].get("slots", {}),
                chat_history[-10:],
                extra_context,
            ):
                ai_response += chunk
                buffer += chunk
                if len(buffer) >= 5 or any(
                    p in buffer for p in ["。", "！", "？", ".", "!", "?", "\n"]
                ):
                    for char in buffer:
                        yield char
                        if char in ["。", "！", "？", ".", "!", "?"]:
                            await asyncio.sleep(0.1)
                        else:
                            await asyncio.sleep(0.01)
                    buffer = ""  # 清空缓冲区
                    await asyncio.sleep(0.02)
            # 抛出剩余字符
            if buffer:
                for char in buffer:
                    yield char
                    await asyncio.sleep(0.02)

            query_recommend_content = await query_recommend.process(
                user_input, chat_history, state.intent
            )
            if query_recommend_content:
                ai_response += f"\n\n{query_recommend_content}"
                recommend = True
                separator = "\n\n"
                yield separator
                for char in query_recommend_content:
                    yield char
                    await asyncio.sleep(0.02)

        elif action_result["action"] == "collect_slots":
            intent = action_result["intent"]
            ai_response = action_result["response"]
            for char in ai_response:
                yield char
                await asyncio.sleep(0.02)

        else:
            intent = "unknown"
            ai_response = action_result["response"]
            query_recommend_content = await query_recommend.process(
                user_input, chat_history, action_result["params"].get("intent", "")
            )
            if query_recommend_content:
                ai_response += f"\n\n{query_recommend_content}"
                recommend = True
            yield ai_response
        state.add_history("user_input", user_input)
        state.add_history("assistant", ai_response)
        self.chat_dao.save_round_of_conv(conv_id, state, ai_response, intent, recommend)

    # 检索工作记忆的意图历史
    def _get_intent_history(self, chat_history: list) -> str:
        if not chat_history:
            print("工作记忆为空")
            return "无"

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
        return intent_history_json


dialogue_manager = DialogueManager()
