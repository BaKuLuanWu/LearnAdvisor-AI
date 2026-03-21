from src.config.prompt.intent import (
    COURSE_QUERY_AND_ANSWER,
    PROFESSIONAL_CONSULTING,
    FILE_CONTENT_QUERY,
    DAILY_CHAT,
)
import os
from langchain_openai import ChatOpenAI
import asyncio
from src.infra.search_tool import search_tool
from src.dao import chat_dao
from src.service.upload_file_service import UploadFileService
from src.config import setup_logging

logger = setup_logging()


class ReplyModule:

    def __init__(self):

        self.search_tool = search_tool

        self.chat_dao = chat_dao

        self.llm = ChatOpenAI(
            model="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.4
        )

    async def process(
        self,
        conv_id: str,
        user_input: str,
        intent: str,
        chat_history: list,
        extra_context: str,
    ):
        print("-------")
        logger.info(f"当前意图为:{intent}")
        print("-------")

        if intent == "daily_chat":
            prompt = DAILY_CHAT.format(extra_context=extra_context)

        elif intent == "file_content_query":
            upload_file_service = UploadFileService(conv_id)
            knowledge = upload_file_service.get_knowledge(user_input)
            prompt = FILE_CONTENT_QUERY.format(
                extra_context=extra_context, knowledge=knowledge
            )

        else:
            docs = self.chat_dao.get_documents(user_input)
            knowledge = ""
            i = 0
            for doc in docs:
                i += 1
                knowledge += f"\n{i}:{doc.get("content",'未知内容或内容无法识别')}"

            if intent == "course_query_and_answer":
                prompt = COURSE_QUERY_AND_ANSWER.format(
                    extra_context=extra_context, knowledge=knowledge
                )

            else:
                search_result = self.search_tool.process(user_input)
                knowledge_context = (
                    f"系统课程知识库:{knowledge}\n网络搜索结果:{search_result}"
                )
                prompt = PROFESSIONAL_CONSULTING.format(
                    extra_context=extra_context, knowledge=knowledge_context
                )

        async for chunk in self._get_ai_response_simple(user_input, prompt, chat_history):
            yield chunk

    # 近期记忆只有最近五轮
    async def _get_ai_response_simple(self, user_input, prompt, chat_history):
        print(f"\n提示词查看:\n{prompt}")
        print(f"近期记忆长度:{len(chat_history)}")
        messages = [{"role": "system", "content": prompt}]

        i = 1
        for msg in chat_history:
            print(f"消息{i}:  {msg.role}  {msg.content[:20]}")
            messages.append({"role": msg.role, "content": msg.content})
            i += 1

        messages.append({"role": "user", "content": user_input})

        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content
                await asyncio.sleep(0)
