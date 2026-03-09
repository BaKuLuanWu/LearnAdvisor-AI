import random
import asyncio
from src.config.static.question_recommend import (
    COURSE_TEMPLATE,
    PROFESSION_TEMPLATE,
    FILE_UPLOAD,
    DAILY_CHAT,
    OPENING_LINE,
)
from src.config.static.subject import SUBJECT_LIST
from src.infra.vector_store import VectorStore
from src.dao import chat_dao
from langchain_core.documents import Document
from datetime import datetime


class QueryRecommend:

    def __init__(self, timeout=2):
        self.timeout = timeout

        self.chat_dao = chat_dao
        self.title_vector_store = VectorStore("title")
        if self.title_vector_store.collection.count() == 0:
            docs = []
            for subject in SUBJECT_LIST:
                doc = Document(
                    page_content=subject,
                    metadata={"import_time": datetime.now().isoformat()},
                )
                docs.append(doc)
            self.title_vector_store.add_documents(docs)

    def _context_handle(self, chat_history: list):
        # 查看最近20轮对话
        context = []
        for idx, msg in enumerate(chat_history[-40:]):
            if msg.role == "user" and msg.intent:
                obj = {"intent": msg.intent, "recommend": False}
                if (
                    chat_history[idx + 1].role == "assistant"
                    and chat_history[idx + 1].recommend
                ):
                    obj["recommend"] = True

                context.append(obj)

        print("上下文推荐情况:")
        for obj in context:
            print(obj["intent"] + " " + str(obj["recommend"]))

        return context

    # 根据上下文来决定推荐问题的频率和数量
    def _get_frequency_and_quantity(self, context: list, intent: str):
        """
        根据上下文历史对话，动态调整：
        1. 推荐概率（通过随机种子 frequency 控制）
        2. 推荐数量（1-5个问题）

        :param context: 历史对话上下文
        :param intent: 当前轮用户的意图
        :return: (frequency, quantity)
                frequency: 作为随机种子，值越大推荐概率越高（比如范围1-10）
                quantity: 推荐的问题数量（1-5）
        """
        # 基础设置
        BASE_FREQ = 5  # 基准随机种子（对应50%推荐概率）
        BASE_QUANT = 3  # 基准推荐数量

        # 概率映射表（frequency -> 推荐概率）
        # 1->10%, 2->20%, 3->30%, 4->40%, 5->50%,
        # 6->60%, 7->70%, 8->80%, 9->90%, 10->100%

        if not context:
            return BASE_FREQ, BASE_QUANT

        # ---------- 宏观调整：根据历史推荐占比 ----------
        # 计算历史中实际推荐的比例
        true_count = sum(1 for obj in context if obj.get("recommend", False))
        ratio_true = true_count / len(context)

        # 期望的推荐比例设定在30%-50%之间
        TARGET_MIN = 0.3
        TARGET_MAX = 0.5

        # 根据历史推荐比例调整frequency
        if ratio_true > TARGET_MAX:
            # 历史推荐太多，降低推荐概率
            freq_adjustment = -2  # frequency减2，降低20%概率
            print("历史推荐太多，降低推荐概率")
        elif ratio_true < TARGET_MIN:
            # 历史推荐太少，提高推荐概率
            print("历史推荐太少，提高推荐概率")
            freq_adjustment = +2  # frequency加2，提高20%概率
        else:
            freq_adjustment = 0

        # ---------- 微观调整：根据最近几轮与当前意图 ----------
        recent_window = 3
        recent_objs = context[-recent_window:]

        # 特殊情况：连续unknown且未推荐，需要大幅提高推荐概率
        if intent == "unknown":
            # 检查最近几轮unknown未推荐的情况
            unknown_no_recommend_count = sum(
                1
                for obj in recent_objs
                if obj.get("intent") == "unknown" and not obj.get("recommend", False)
            )

            if unknown_no_recommend_count >= 2:
                # 最近3轮中有2轮以上是unknown且未推荐，大幅提高推荐概率
                print("最近3轮中有2轮以上是unknown且未推荐，大幅提高推荐概率")
                freq_adjustment += 3
            elif unknown_no_recommend_count >= 1:
                # 有1轮是unknown且未推荐，适当提高
                freq_adjustment += 1
                print("有1轮是unknown且未推荐，适当提高")

        # 如果当前意图明确且历史推荐正常，可以适当降低推荐概率避免打扰
        elif intent != "unknown" and TARGET_MIN <= ratio_true <= TARGET_MAX:
            if any(obj.get("intent") == intent for obj in recent_objs):
                # 最近几轮出现过相同意图，可能用户已经清楚，适当降低推荐
                freq_adjustment -= 1

        # ---------- 计算最终的frequency ----------
        # 确保frequency在1-10范围内（对应10%-100%推荐概率）
        frequency = max(1, min(10, BASE_FREQ + freq_adjustment))

        # ---------- 根据情况调整推荐数量 ----------
        # 推荐数量可以跟推荐概率正相关
        if frequency <= 3:
            # 低概率推荐时，数量也少（1-2个）
            quantity = max(1, min(2, BASE_QUANT))
        elif frequency >= 8:
            # 高概率推荐时，数量也多（4-5个）
            quantity = max(4, min(5, BASE_QUANT + 1))
        else:
            # 正常情况，2-4个
            quantity = max(2, min(4, BASE_QUANT))

        return frequency, quantity

    async def process(self, user_input: str, chat_history: list, intent: str):

        context = self._context_handle(chat_history)
        frequency, quantity = self._get_frequency_and_quantity(context, intent)
        print(f"当前概率:{frequency}")

        result = None
        # 满足一定概率才推荐
        if random.randint(1, 10) <= frequency:
            print("有调用")
            questions = await self._get_questions(user_input, intent, quantity)
            print("随机生成的推荐问题:")
            for q in questions:
                print(q)

            result = random.choice(OPENING_LINE)
            for idx, question in enumerate(questions):
                result += f"\n{idx+1}.{question}"
            print(result)
        return result

    # 根据不同意图来决定推荐问题的内容来源
    async def _get_questions(self, user_input: str, intent: str, quantity: int):
        if intent == "course_query_and_answer":
            selected_templates = random.sample(COURSE_TEMPLATE, quantity)
            selected_titles = []
            try:
                knowledge_list = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.title_vector_store.search, user_input, quantity
                    ),
                    timeout=self.timeout,
                )
                selected_titles = [k["content"] for k in knowledge_list]
            except asyncio.TimeoutError:
                print("向量检索超时")
                selected_titles = random.sample(SUBJECT_LIST, quantity)

            questions = [
                template.format(title=title)
                for template, title in zip(selected_templates, selected_titles)
            ]
            return questions

        elif intent == "professional_consulting":
            selected_templates = random.sample(PROFESSION_TEMPLATE, quantity)
            selected_titles = []
            try:
                knowledge_list = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.title_vector_store.search, user_input, quantity
                    ),
                    timeout=self.timeout,
                )
                selected_titles = [k["content"] for k in knowledge_list]
            except asyncio.TimeoutError:
                print("向量检索超时")
                selected_titles = random.sample(SUBJECT_LIST, quantity)

            questions = [
                template.format(title=title)
                for template, title in zip(selected_templates, selected_titles)
            ]
            return questions

        elif intent == "file_content_query":
            return random.sample(FILE_UPLOAD, quantity)

        elif intent == "daily_chat":
            try:
                entity_list = await asyncio.wait_for(
                    self.chat_dao.get_hot_questions(quantity), timeout=0.5
                )
                questions = [entity.content for entity in entity_list]
            except asyncio.TimeoutError:
                print("数据库检索超时")
                questions = random.sample(DAILY_CHAT, quantity)

            return questions

        # 当意图为unknown
        else:
            titles = random.sample(SUBJECT_LIST, 10)

            questions = (
                [
                    t.format(title=title)
                    for t, title in zip(random.sample(COURSE_TEMPLATE, 5), titles[:5])
                ]
                + [
                    t.format(title=title)
                    for t, title in zip(
                        random.sample(PROFESSION_TEMPLATE, 5), titles[5:]
                    )
                ]
                + random.sample(FILE_UPLOAD, 2)
                + random.sample(DAILY_CHAT, 2)
            )

            print("意图为unknown时的问题列表:")
            for q in questions:
                print(q)

            return random.sample(questions, quantity)


query_recommend = QueryRecommend()
