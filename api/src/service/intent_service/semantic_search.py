import os
from langchain_openai import ChatOpenAI
from src.dao import intent_dao
from src.model.schema.intent_schema import RuleResult
from collections import OrderedDict
import json
from typing import Dict, Any, Optional
from src.config.prompt.intent import INTENT_RECOGNITION_PROMPT
from src.infra.search_tool import search_tool
import time
from src.config.settings import setup_logging

logger = setup_logging()


class LRUCache:
    """简单的LRU缓存实现"""

    def __init__(self, maxsize: int = 1000):
        self.cache = OrderedDict()
        self.maxsize = maxsize

    def __contains__(self, key):
        return key in self.cache

    def __getitem__(self, key):
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def __setitem__(self, key, value):
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        self.cache[key] = value


class SemanticSearch:
    def __init__(self):

        # 使用小规格LLM
        self.llm = ChatOpenAI(
            model="qwen2.5-3b-instruct",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        self.dao = intent_dao

        # LLM缓存（减少调用次数）
        self.cache = LRUCache(maxsize=1000)

        self.agent = IntentRecognitionAgent()

    def analyze(
        self, user_input: str, intent_history: str, rule_result: RuleResult
    ) -> RuleResult:
        """LLM辅助分析 - 处理规则无法覆盖的情况"""

        # 内存检索
        if user_input in self.cache:
            return self.cache[user_input]

        # 向量数据库检索
        similar_q = self.dao.vector_search(user_input, k=3)
        if similar_q and similar_q[0]["score"] > 0.85:
            # 找到高度相似的历史问题，直接使用已知答案
            print(similar_q[0])
            logger.info("\n向量库找到相似意图结果")
            return RuleResult(
                intent=similar_q[0].get("metadata", {}).get("intent", "unknown"),
                confidence=0.9,
            )

        # LLM检索
        try:
            result = self.agent.recognize_intent(
                user_input=user_input,
                intent_history=intent_history,
                rule_result=rule_result.__dict__,
            )
            logger.info(f'\n意图识别原因:\n{result["reason"]}')

            # 明确识别出意图的才被保存
            if result["intent"] != "unknown":
                """self.dao.add_query_and_pending_intent_vector(
                    user_input, result["intent"]
                )"""
                pass
            print(
                f'小模型输出结果: 意图:{result['intent']} 复杂度:{result["confidence"]}'
            )
            return RuleResult(result["intent"], result["confidence"])
        except Exception as e:
            # LLM失败时，返回安全降级结果
            print(e)
            return RuleResult(
                intent="unknown",
                confidence=0.0,
            )


class IntentRecognitionAgent:
    def __init__(self):

        self.llm = ChatOpenAI(
            model="qwen2.5-3b-instruct",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.search_tool = search_tool
        self.confidence_threshold = 0.6

    def recognize_intent(
        self,
        user_input: str,
        intent_history: str,
        rule_result: str,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """
        主流程：识别意图，低置信度时自动调用搜索
        """
        attempts = 0
        context = ""  # 搜索结果的上下文

        while attempts < max_retries:
            attempts += 1
            print(f"执行次数:{attempts}")
            # 步骤1: 调用模型判断意图
            intent_result = self._call_intent_model(
                user_input, intent_history, rule_result, context
            )

            # 步骤2: 检查置信度
            if (
                intent_result.get("intent", "") != "unknown"
                and intent_result.get("confidence", 0) >= self.confidence_threshold
            ):
                return self._format_final_result(
                    intent_result, searched=(context != "")
                )

            # 步骤3: 置信度不足，调用搜索
            if attempts < max_retries and intent_result.get("needs_search", False):
                search_query = intent_result.get("search_query") or user_input
                context = self.search_tool.process(search_query)
            else:
                # 达到重试次数或不需要搜索
                print("达到重试次数或不需要搜索")
                return {
                    "intent": "unknown",
                    "confidence": intent_result.get("confidence", 0),
                    "reason": "无法确定意图",
                    "searched": (context != ""),
                    "final": True,
                }

    def _call_intent_model(
        self, user_input: str, history: str, rule_result: str, context: str = ""
    ) -> Dict[str, Any]:
        """调用大模型进行意图识别"""

        prompt = self._build_prompt(user_input, history, rule_result, context)
        print(f"提示词具体内容:\n{prompt}")
        try:
            response = self.llm.invoke(prompt)
            ai_msg = response.content
            print(f"模型意图识别结果:{ai_msg}")

            # 如果包含Markdown代码块，去掉
            if ai_msg.startswith("```json"):
                ai_msg = ai_msg.replace("```json", "", 1)
            if ai_msg.endswith("```"):
                ai_msg = ai_msg[:-3]
            print(f"清理后的结果:{ai_msg}")

            # 解析JSON响应
            result = json.loads(ai_msg)
            print(f"json格式化后:{result}")

            # 验证必要字段
            if "intent" not in result or "confidence" not in result:
                result = {"intent": "unknown", "confidence": 0.0}
            return result

        except json.JSONDecodeError:
            print("模型没返回JSON，尝试提取或返回默认")
            return self._parse_fallback_response(response.content)

    def _build_prompt(
        self, user_input: str, history: str, rule_result: str, context: str = ""
    ) -> str:
        """构建提示词"""
        base_prompt = INTENT_RECOGNITION_PROMPT.format(
            history=history, rule_result=rule_result, user_input=user_input
        )

        if context:
            print(f"——————有网络搜索结果——————\n{context}")
            base_prompt += f"\n## 网络搜索获取的上下文信息：\n{context}\n请基于以上搜索上下文，重新判断问题的意图。"

        base_prompt += "\n请输出JSON格式："
        return base_prompt

    def _parse_fallback_response(self, text_response: str) -> Dict[str, Any]:
        """解析非JSON响应"""
        # 尝试从文本中提取意图关键词
        intent_keywords = {
            "course_query_and_answer": ["课程", "内容", "大纲", "评分"],
            "professional_consulting": ["工作", "就业", "薪资", "前景"],
            "file_content_query": ["论文", "文档", "总结", "归纳"],
            "daily_chat": ["你好", "谢谢", "天气", "计算"],
        }

        if any(key in text_response for key in intent_keywords.keys()):
            return {"intent": intent, "confidence": 0.5, "needs_search": True}

        for intent, keywords in intent_keywords.items():
            if any(keyword in text_response for keyword in keywords):
                return {"intent": intent, "confidence": 0.5, "needs_search": True}

        return {"intent": "unknown", "confidence": 0.0, "needs_search": True}

    def _format_final_result(
        self, intent_result: Dict[str, Any], searched: bool = False
    ) -> Dict[str, Any]:
        """格式化最终结果"""
        return {
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "reason": intent_result.get("reason", ""),
            "searched": searched,
            "final": True,
            "metadata": {
                "threshold_used": self.confidence_threshold,
                "timestamp": time.time(),
            },
        }


semantic_search = SemanticSearch()
