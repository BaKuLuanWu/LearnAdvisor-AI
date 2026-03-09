from fastapi import APIRouter
from src.infra.vector_store import intent_vector_store
from src.common.util import Result

router = APIRouter(prefix="/admin", tags=["管理"])


@router.post("/clear-intent-vector-store")
def clear_intent_vector_store():
    print("正在清空意图识别向量数据库...")

    intent_vector_store.clear()

    return Result.ok(message="清空成功")
