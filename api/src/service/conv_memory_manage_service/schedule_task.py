from langchain_openai import ChatOpenAI
from src.model.schema.chat_schema import Summary
from src.config.prompt.conv_memory_manage import SUMMARY_LEVEL1, SUMMARY_LEVEL2
from src.dao import conv_memory_manage_dao
import os
import json
import schedule
import time
import threading
from src.config.settings import setup_logging

logger = setup_logging()


class ScheduleTask:

    def __init__(self):
        self.dao = conv_memory_manage_dao

        self.llm = ChatOpenAI(
            model="qwen-turbo",  # 保证轻量级的同时生成质量高
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        self.large_llm = ChatOpenAI(
            model="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        self.cache = {}
        print("定时器启动！")

        schedule.every(2).minutes.do(lambda: self.process(True))
        # 启动调度线程
        self._start_schedule_thread()

    def _start_schedule_thread(self):
        def run():
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        print("调度线程已启动")

    def process(self, open: bool):
        try:
            conv_ids = self.dao.get_conv_ids()
            for conv_id in conv_ids:
                if conv_id not in self.cache:
                    self.cache[conv_id] = {"lv1_summary_count": 0}
                print(
                    f"当前对话id为:{conv_id},一级摘要的次数为:{self.cache[conv_id]["lv1_summary_count"]}"
                )

                start_index1, end_index1 = self._need_summary_level1(conv_id)
                if start_index1 and end_index1:
                    self._generate_summary_level1(conv_id, start_index1, end_index1)
                    self.cache[conv_id]["lv1_summary_count"] += 1
                else:
                    print("目前无需要一级摘要的对话")

                if self.cache[conv_id]["lv1_summary_count"] % 6 == 0 or open:
                    start_index2, end_index2 = self._need_summary_level2(conv_id)
                    if not start_index2 or not end_index2:
                        print("目前无需要二次摘要的对话")
                    else:
                        self._generate_summary_level2(conv_id)
        except Exception as e:
            logger.error(f"定时任务出错，原因为:{e}")

    def _need_summary_level1(self, conv_id: str) -> tuple[int, int]:
        max_turn = self.dao.get_max_turn(conv_id) or 0
        print(f"消息表中最大轮次:{max_turn}")
        recent_summary = self.dao.get_recent_summary(conv_id)
        print(f"摘要表中最大轮次:{max_turn}")
        if max_turn < 6:
            return 0, 0
        elif not recent_summary:
            return (1, max_turn - 5)
        # 保留最近五轮作为工作记忆
        elif max_turn - recent_summary.end_index > 5:
            return (recent_summary.end_index + 1, max_turn - 5)
        else:
            return 0, 0

    def _generate_summary_level1(self, conv_id: str, start_index: int, end_index: int):
        print("正在生成一级摘要...")

        messages = self.dao.get_messages_by_range(conv_id, start_index, end_index)
        prompt_msg = {"role": "system", "content": SUMMARY_LEVEL1}
        user_input = ""
        summaries = []

        for i, msg in enumerate(messages):
            if msg.role == "user":
                ai_text = messages[i + 1].content.replace("\n", "")
                new_text = f"\n对话{msg.turn}: 用户:{msg.content} 助手:{ai_text}"
                print(f"用户输入长度:{len(user_input)}")

                if len(user_input + new_text) > 10000:
                    response = self.llm.invoke(
                        [prompt_msg, {"role": "user", "content": user_input}]
                    ).content
                    print(f"摘要结果:{response}")
                    try:
                        result = json.loads(response)
                        values = result["list"]
                        for v in values:
                            summary = Summary(
                                v["turn"], v["turn"], v["content"], conv_id, 1, True
                            )
                            summaries.append(summary)
                        user_input = new_text
                        print(f"清空输入:{user_input}")
                    except json.JSONDecodeError:
                        logger.error(f"操作失败，错误为{e}")
                        print("模型没返回JSON，任务执行失败！")

                    if i == len(messages) - 2:
                        response = self.llm.invoke(
                            [prompt_msg, {"role": "user", "content": new_text}]
                        ).content
                        print(f"摘要结果:{response}")
                        try:
                            result = json.loads(response)
                            values = result["list"]
                            for v in values:
                                summary = Summary(
                                    v["turn"], v["turn"], v["content"], conv_id, 1, True
                                )
                                summaries.append(summary)
                            user_input = ""
                            print(f"清空输入:{user_input}")
                        except json.JSONDecodeError as e:
                            logger.error(f"操作失败，错误为{e}")
                            print("模型没返回JSON，任务执行失败！")

                elif i == len(messages) - 2:
                    user_input += new_text
                    response = self.llm.invoke(
                        [prompt_msg, {"role": "user", "content": user_input}]
                    ).content
                    print(f"摘要结果:{response}")
                    try:
                        result = json.loads(response)
                        values = result["list"]
                        for v in values:
                            summary = Summary(
                                v["turn"], v["turn"], v["content"], conv_id, 1, True
                            )
                            summaries.append(summary)
                        user_input = ""
                        print(f"清空输入:{user_input}")
                    except json.JSONDecodeError as e:
                        logger.error(f"操作失败，错误为{e}")
                        print("模型没返回JSON，任务执行失败！")
                else:
                    user_input += new_text

        self.dao.add_summaries(summaries)
        print("生成完毕")

    def _need_summary_level2(self, conv_id: str) -> tuple[int, int]:
        lv1_end_index = self.dao.get_recent_summary_level1_end_index(conv_id) or 0
        lv2_end_index = self.dao.get_recent_summary_level2_end_index(conv_id) or 0
        if lv1_end_index - lv2_end_index > 14:
            return (lv2_end_index + 1, lv1_end_index)
        else:
            return (0, 0)

    def _generate_summary_level2(self, conv_id: str):
        print("正在生成二级摘要...")
        level1_summaries = self.dao.get_summary_level1_list(conv_id)
        prompt_msg = {"role": "system", "content": SUMMARY_LEVEL2}
        user_input = ""
        level2_summaries = []
        current_turn = level1_summaries[0].start_index
        max_turn = level1_summaries[-1].start_index
        start_index = current_turn
        end_index = max_turn
        print(f"最大一级摘要轮次:{max_turn}")

        while max_turn - current_turn > 10:
            print(f"当前对话轮次:{current_turn}")
            j = 0
            for summary in level1_summaries:
                if current_turn <= summary.start_index and j < 5:
                    print(f"执行次数:{j}")
                    j += 1
                    user_input += f"\n对话{summary.start_index}: {summary.content}"
                if j == 5:
                    break
            print(f"用户输入:{user_input}")
            response = self.llm.invoke(
                [prompt_msg, {"role": "user", "content": user_input}]
            ).content
            print(f"摘要结果:{response}")
            try:
                result = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"操作失败，错误为{e}")
                print("模型没返回JSON，任务执行失败！")
            user_input = ""
            level2_summary = Summary(
                current_turn, result["max_turn"], result["summary"], conv_id, 2, True
            )
            level2_summaries.append(level2_summary)
            end_index = result["max_turn"]
            current_turn = result["max_turn"] + 1

        self.dao.add_lv2_summaries(level2_summaries, conv_id, start_index, end_index)
        print("生成完毕")

    def _generate_user_persona():
        pass

    def _save_key_sentence():
        pass


schedule_task = ScheduleTask()
