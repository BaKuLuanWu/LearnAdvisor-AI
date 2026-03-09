from pydantic import BaseModel
from typing import List, Optional


class ChatQueryDTO(BaseModel):
    user_id:str  # 用户身份决定部分功能开放
    conv_id: str 
    user_input: str
    files: Optional[List[str]] = None
