"""
API客户端 - 调用后端API
"""

import json
import requests
from typing import Dict, List, Optional


class APIClient:
    def __init__(self, base_url="http://localhost:8000/chat"):
        self.base_url = base_url
        self.user_id = "019bf364-e196-71cd-9522-e0f49d773f7d"

    def get_grouped_conversations(self) -> Dict:
        """获取分组对话历史"""
        try:
            response = requests.get(
                f"{self.base_url}/get/conversation/list/{self.user_id}"
            )

            print(f"获取历史对话列表接口响应:{response.json()}")
            return response.json()["data"]
        except:
            return None

    def create_conversation(self, title="新对话") -> Dict:
        """创建新对话"""
        try:
            response = requests.post(
                f"{self.base_url}/create/conversation",
                json={
                    "user_id": self.user_id,
                    "title": title,
                },
            )

            print(f"创建新对话响应:{response.json()}")
            return response.json()["data"]

        except:
            # 模拟API返回
            return None

    def get_conversation_detail(self, conv_id: str) -> Dict:
        """获取特定对话详情"""
        try:
            response = requests.get(f"{self.base_url}/get/conversation/{conv_id}")

            return response.json()["data"]

        except:
            return None

    def chat(
        self, conv_id: str, user_input: str, files: Optional[List[str]] = None
    ) -> str:
        """调用AI聊天接口"""
        try:
            payload = {
                "user_id": self.user_id,
                "conv_id": conv_id,
                "user_input": user_input,
            }
            if files:
                payload["files"] = files

            response = requests.post(f"{self.base_url}", json=payload)

            print(f"聊天接口响应:{response.json()}")
            return response.json()["data"]
        except:
            return None

    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/conversations/{conversation_id}"
            )
            return response.status_code == 200
        except:
            # 模拟API返回
            print(f"[API] 删除对话 {conversation_id}")
            return True
