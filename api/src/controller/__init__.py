from fastapi import APIRouter
from . import chat_controller, user_controller, admin_controller

api_router = APIRouter()

api_router.include_router(chat_controller.router)
api_router.include_router(user_controller.router)
api_router.include_router(admin_controller.router)

__all__ = ["api_router"]
