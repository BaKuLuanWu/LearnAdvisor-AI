from src.config.static.subject import SUBJECTS, SUBJECT_LIST


class TitleMatch:
    """标签搜索规则引擎：识别用户输入中的课程及意图类型"""

    # 意图关键词
    course_keywords = ["课程", "课", "教学"]
    profession_keywords = [
        "行业",
        "市场",
        "前景",
        "发展",
        "领域",
        "方面",
        "学习路线",
        "学习规划",
        "就业",
        "薪资",
        "职业发展",
        "岗位",
    ]

    def __init__(self):
        """初始化时构建课程关键词库"""
        self.course_list = self._build_course_list()

    # ---------- 内部工具方法 ----------
    @staticmethod
    def _extract_keywords(course_str):
        """
        从课程原始字符串中提取所有可能的关键词（英文、中文、分割项）
        返回关键词列表
        """
        keywords = []
        # 分离英文部分和括号内的中文部分
        if "（" in course_str and "）" in course_str:
            eng_part = course_str[: course_str.index("（")]
            chi_part = course_str[course_str.index("（") + 1 : course_str.index("）")]
        else:
            eng_part = course_str
            chi_part = ""

        # 处理英文部分（按 '/' 分割）
        for item in eng_part.split("/"):
            item = item.strip()
            if item:
                keywords.append(item)
        # 处理中文部分（按 '/' 分割）
        for item in chi_part.split("/"):
            item = item.strip()
            if item:
                keywords.append(item)

        return keywords

    def _build_course_list(self):
        """生成课程列表，每个元素为 (原始名称, 关键词列表)"""
        course_list = []
        for category, courses in SUBJECTS.items():
            key = self._extract_keywords(category)
            course_list.append(key[0])
            for course in courses:
                values = self._extract_keywords(course)
                for val in values:
                    course_list.append(val)
        return course_list

    # ---------- 核心规则引擎 ----------
    def process(self, user_input: str):
        input_lower = user_input.lower()

        # 查找第一个匹配的课程
        matched_keyword = None
        end_idx = None

        for keyword in SUBJECT_LIST:
            kw_lower = keyword.lower()

            pos = input_lower.find(kw_lower)
            if pos != -1:
                if "学" in user_input[pos - 2 : pos]:
                    print("是课程咨询")
                    return None
                matched_keyword = keyword
                print(f"位置:{pos}")
                end_idx = pos + len(kw_lower)
                break

        if not matched_keyword:
            return None  # 未匹配任何title

        # 从匹配关键词之后的部分搜索意图词
        after_text = user_input[end_idx:]
        print(f"后续内容:{after_text}")

        has_course = any(kw in after_text for kw in self.course_keywords)
        has_profession = any(kw in after_text for kw in self.profession_keywords)

        if has_course == has_profession:
            # 都没有 或 两者都有 → 意图不明确
            return matched_keyword
        else:
            return None


title_match = TitleMatch()
