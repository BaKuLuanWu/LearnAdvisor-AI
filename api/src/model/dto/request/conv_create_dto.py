from pydantic import BaseModel

class ConversationCreate(BaseModel):
    user_id : str
    title: str = "新对话"
