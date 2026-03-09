from langchain_tavily import TavilySearch
from typing import Dict, Any
from src.config import setup_logging
import os

os.environ["TAVILY_API_KEY"] = "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"
logger = setup_logging()


class SearchTool:
    def __init__(self):
        self.search = TavilySearch(max_results=2)

    def process(self, search_query: str):
        search_results = self._perform_search(search_query)
        return self._summarize_search_results(search_results)

    def _perform_search(self, query: str) -> Dict[str, Any]:
        """调用搜索插件"""
        try:
            logger.info(f"原始搜索语句:{query}")
            # 优化搜索查询
            optimized_query = self._optimize_search_query(query)
            logger.info(f"优化后的搜索语句:{optimized_query}")

            # 调用搜索插件（假设返回格式化的结果）
            search_results = self.search.run(optimized_query)

            return search_results
        except Exception as e:
            logger.warning(f"搜索失败: {e}")
            return {"error": str(e), "results": []}

    def _optimize_search_query(self, original_query: str) -> str:
        """优化搜索关键词"""
        # 去除常见疑问词
        stop_words = {"吗", "呢", "什么", "怎么", "如何", "是不是", "有没有"}
        words = original_query.split()
        filtered_words = [w for w in words if w not in stop_words]

        # 添加领域限定词（如果需要）
        if len(filtered_words) < 3:
            filtered_words.extend(["课程", "学习", "就业"])

        return " ".join(filtered_words[:5])

    def _summarize_search_results(self, search_results: Dict[str, Any]) -> str:
        """总结搜索结果作为上下文"""
        if "error" in search_results:
            logger.info(f"搜索遇到错误: {search_results['error']}")
            return "未找到相关信息。"

        if not search_results.get("results"):
            return "未找到相关信息。"

        summaries = []
        for i, result in enumerate(search_results["results"][:3], 1):
            title = result.get("title", "无标题")
            content = result.get("content", "")[:40]  # 截断片段
            summaries.append(f"{i}. {title}: {content}")

        return "\n".join(summaries)


search_tool = SearchTool()
