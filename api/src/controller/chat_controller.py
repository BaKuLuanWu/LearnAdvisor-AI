from fastapi import APIRouter
import json
from src.service import conv_memory_manage_service, user_service, chat_service
from src.common.util.function import group_conversations_by_time
from datetime import datetime
from src.model.dto.request import ChatQueryDTO, ConversationCreate
from src.common.util import Result
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.get("/get/conversation/list/{user_id}")
def get_conversation_list(user_id: str):
    """获取分组对话"""

    conv_list = chat_service.get_conversation_list(user_id)
    if conv_list:
        now = datetime.now()

        result = group_conversations_by_time(conv_list, now)

        print("分组结果：\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return Result.ok(result)

    return Result.ok(
        {
            "today": [],
            "yesterday": [],
            "last7days": [],
            "older": [],
        }
    )


@router.get("/get/conversation/{conv_id}")
def get_conversation(conv_id: str):
    """获取对话详情"""

    conv = chat_service.get_conversation_detail(conv_id)
    if conv:
        return Result.ok(conv)

    return Result.error(message="对话不存在")


@router.post("/create/conversation")
def create_conversation(conv: ConversationCreate):
    """创建新对话"""

    # isoformat 会包含毫秒，去掉毫秒部分
    # formatted_time = datetime.now().isoformat(timespec="seconds")

    conv_id = chat_service.create_conversation(conv.user_id, conv.title)

    return Result.ok(conv_id)


@router.post("")
async def chat(dto: ChatQueryDTO):
    """聊天接口"""
    print(f"用户聊天请求:{dto}")

    if user_service.is_vip(dto.user_id):
        priority = "high"  # 优先级
    else:
        priority = "medium"

    chat_history, extra_context = conv_memory_manage_service.get_chat_history_context(
        dto.conv_id, priority
    )

    return StreamingResponse(
        chat_service.chat(dto, chat_history, extra_context),
        media_type="text/plain",
    )
