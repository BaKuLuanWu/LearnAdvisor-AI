import re
from src.model.schema.intent_schema import RuleResult


class RuleEngine:
    """规则引擎:用确定性规则保证核心业务流程100%准确"""

    def __init__(self):
        self.rules = {
            # 课程问答 - 基于课程知识库的直接信息查询
            "course_query_and_answer": {
                "patterns": [
                    # 核心课程查询（必须匹配）
                    (r"课程.*[信息详情]", 55, True),  # 课程信息/详情（必须）
                    (r"什么.*课程", 52, True),  # 什么课程（必须）
                    (r"介绍.*课程", 52, True),  # 介绍课程（必须）
                    # 课程内容查询（新增）
                    (r"课程.*[讲教什么]", 48, False),  # 课程讲什么/教什么
                    (r"内容.*[有哪些是什么]", 48, False),  # 内容有哪些/是什么
                    (r"知识点.*[有哪些]", 46, False),  # 知识点有哪些
                    (r"学习.*[哪些什么]", 46, False),  # 学习哪些内容
                    # 课程属性查询
                    (r"评分.*[多少如何]", 48, False),  # 评分多少/如何
                    (r"难度.*[怎样如何]", 48, False),  # 难度怎样/如何
                    (r"证书.*[类型种类]", 48, False),  # 证书类型/种类
                    (r"机构.*[是什么哪家]", 48, False),  # 机构是什么/哪家
                    # 教学相关查询（新增）
                    (r"[模块章节].*[有哪些]", 44, False),  # 模块/章节有哪些
                    (r"第.*[章节单元]", 42, False),  # 第几章/第几节
                    (r"怎么.*[教学教]", 42, False),  # 怎么教/教学
                    (r"[教学授课].*方式", 40, False),  # 教学/授课方式
                    # 学习资源查询（新增）
                    (r"有.*[视频课件资料]", 40, False),  # 有视频/课件/资料吗
                    (r"[实验实操实践].*内容", 40, False),  # 实验/实操内容
                    (r"[作业习题].*[多少]", 38, False),  # 作业/习题有多少
                    # 通用查询短语
                    (r"关于.*课程", 44, False),  # 关于某课程
                    (r"课程.*[怎么如何]", 44, False),  # 课程怎么样/如何
                    (r"了解.*课程", 42, False),  # 了解某课程
                    # 具体问题格式
                    (r"有.*证书.*吗", 40, False),  # 有证书吗
                    (r"难度.*[大小]", 40, False),  # 难度大小
                    (r"评分.*高", 40, False),  # 评分高吗
                    # 简单查询触发词
                    (r"怎么样", 35, False),  # 怎么样
                    (r"什么", 32, False),  # 什么
                    (r"如何", 30, False),  # 如何
                ],
                "negatives": [
                    r"哪个.*[更好]",  # 比较选择
                    r"怎么.*入门",  # 学习规划
                    r"前景.*如何",  # 职业咨询
                ],
            },
            # 专业咨询 - 职业发展、行业前景、学习规划
            "professional_consulting": {
                "patterns": [
                    # 职业发展核心（必须匹配）
                    (r"职业.*[发展前景]", 60, True),  # 职业发展/前景（必须）
                    (r"就业.*[方向机会]", 60, True),  # 就业方向/机会（必须）
                    (r"行业.*[前景趋势]", 58, True),  # 行业前景/趋势
                    # 能力与价值
                    (r"学完.*能.*[做什么]", 55, False),  # 学完能做什么
                    (r"提升.*[技能能力]", 52, False),  # 提升技能/能力
                    (r"薪资.*[多少水平]", 52, False),  # 薪资多少/水平
                    # 市场需求
                    (r"前景.*[怎样如何]", 50, False),  # 前景怎样/如何
                    (r"需求.*[大吗如何]", 50, False),  # 需求大吗/如何
                    (r"机会.*[多少发展]", 48, False),  # 机会多少/发展
                    # 学习价值判断
                    (r"课程.*[有用]", 46, False),  # 课程有用吗
                    (r"学.*有用.*吗", 46, False),  # 学...有用吗
                    (r"帮助.*[求职转型]", 44, False),  # 帮助求职/转型
                    # 趋势分析
                    (r"未来.*[发展如何]", 42, False),  # 未来发展如何
                    (r"趋势.*[是什么]", 42, False),  # 趋势是什么
                    (r"热门.*[方向领域]", 40, False),  # 热门方向/领域
                    # 咨询类短语
                    (r"建议.*[学习发展]", 38, False),  # 建议学习/发展
                    (r"应该.*[学什么]", 38, False),  # 应该学什么
                    (r"怎么.*[选择]", 36, False),  # 怎么选择
                    # 触发词
                    (r"前景", 35, False),  # 前景
                    (r"就业", 35, False),  # 就业
                    (r"发展", 35, False),  # 发展
                ],
                "negatives": [
                    r"课程.*[信息详情]",  # 纯课程查询
                    r"你好.*吗",  # 日常问候
                ],
            },
            # 基于文件的问答
            "file_content_query": {
                "patterns": [
                    # 核心查询意图（必须匹配）
                    (r"文件.*[讲了什么|内容是什么|说的啥]", 65, True),
                    (r"总结.*[一下|这份|这个]", 65, True),
                    (r"归纳.*[数据|信息|要点]", 63, True),
                    # 具体内容查询
                    (r"这个文件.*[分析|解读]", 60, False),
                    (r"[帮我|请].*概括.*[内容|主旨]", 58, False),
                    (r"提取.*[关键信息|重点]", 56, False),
                    # 基于文件的知识问答
                    (r"根据.*文件.*回答.*[问题]", 55, False),
                    (r"文件里.*提到.*[什么|如何]", 54, False),
                    (r"基于.*文档.*[分析|讨论]", 53, False),
                    # 不同类型文件的查询
                    (r"论文.*[摘要|结论]", 52, False),
                    (r"表格.*[数据|统计]", 52, False),
                    (r"报告.*[主要观点|发现]", 50, False),
                    # 结构化和细化查询
                    (r"列出.*[要点|重点]", 48, False),
                    (r"[分析|解析].*图表", 47, False),
                    (r"对比.*文件.*[内容]", 46, False),
                    # 应用导向查询
                    (r"文件.*[建议|方案]", 45, False),
                    (r"从.*中.*[学习到什么]", 44, False),
                    (r"如何.*应用.*[文件内容]", 42, False),
                    # 触发词
                    (r"总结", 40, False),
                    (r"归纳", 38, False),
                    (r"概括", 38, False),
                    (r"提取", 36, False),
                    (r"分析", 36, False),
                    # 组合查询（结合专业咨询）
                    (r"根据文件.*[前景|趋势]", 55, False),
                    (r"文档中.*[发展|机会]", 53, False),
                    (r"基于.*报告.*[建议|规划]", 50, False),
                ],
                # 询问上传操作
                "negatives": [
                    r"怎么上传",
                    r"上传失败",
                    r"文件大小",
                    r"支持什么格式",
                    r"能传几个文件",
                    r"没有文件",
                ],
            },
            # 日常交流 - 问候、常识、通用对话
            "daily_chat": {
                "patterns": [
                    # 问候类（必须匹配）
                    (r"^(你好|您好|嗨|hello|hi|hey)", 70, True),  # 开头问候（必须）
                    (r"(早上好|下午好|晚上好)", 65, False),  # 时间问候
                    # 天气查询（新增）
                    (r"今天.*天气", 60, False),  # 今天天气
                    (r"明天.*天气", 60, False),  # 明天天气
                    (r"天气.*如何", 58, False),  # 天气如何
                    (r"气温.*多少", 58, False),  # 气温多少
                    # 常识问答（新增）
                    (r"什么是.*", 56, False),  # 什么是...（常识类）
                    (r".*是什么意思", 56, False),  # ...是什么意思
                    (r"请.*解释.*", 54, False),  # 请解释...
                    (r"简单.*问题", 52, False),  # 简单问题
                    # 数学计算（新增）
                    (r"计算.*", 50, False),  # 计算...
                    (r".*等于多少", 50, False),  # ...等于多少
                    (r"数学题", 48, False),  # 数学题
                    (r"算一下", 48, False),  # 算一下
                    # 生活咨询（新增）
                    (r"建议.*[吃饭旅游]", 46, False),  # 建议吃饭/旅游
                    (r"推荐.*[电影音乐]", 46, False),  # 推荐电影/音乐
                    (r"怎么.*[做]", 44, False),  # 怎么做...
                    # 感谢与礼貌
                    (r"(谢谢|多谢|感谢)", 65, False),  # 感谢
                    (r"(再见|拜拜|下次聊)", 65, False),  # 结束
                    (r"(不客气|不用谢)", 60, False),  # 回应感谢
                    # 简单交流
                    (r"今天.*[怎么样]", 55, False),  # 今天怎么样
                    (r"你.*[好吗]", 55, False),  # 你好吗
                    (r"最近.*如何", 52, False),  # 最近如何
                    # 情感表达
                    (r"(哈哈|呵呵|嘿嘿)", 50, False),  # 笑声
                    (r"(嗯|哦|好的|OK)", 48, False),  # 回应词
                    # 通用触发词
                    (r"请问", 46, False),  # 请问
                    (r"麻烦你", 44, False),  # 麻烦你
                    (r"帮我", 44, False),  # 帮我
                ],
                "negatives": [
                    r"课程.*[信息|内容]",  # 课程相关内容
                    r"职业.*发展",  # 职业发展
                    r"就业.*方向",  # 就业方向
                ],
            },
        }

        # 阈值设置
        self.MIN_CONFIDENCE = 0.6
        self.MAX_SCORE = 100

    def match_intent(self, text) -> RuleResult:
        """
        智能匹配意图
        """
        best_intent = "unknown"
        best_score = 0

        for intent_name, intent_config in self.rules.items():
            score = self._calculate_score(text, intent_config)

            if score > best_score:
                best_score = score
                best_intent = intent_name

        # 转换为置信度
        confidence = best_score / self.MAX_SCORE

        if confidence < self.MIN_CONFIDENCE:
            return RuleResult("unknown", 0.0)

        return RuleResult(best_intent, confidence)

    def _calculate_score(self, text, config):
        """
        计算一个意图的得分
        """
        score = 0
        must_have_matched = False

        # 1. 检查否定词（一票否决）
        for neg_pattern in config["negatives"]:
            if re.search(neg_pattern, text):
                return 0  # 有否定词，直接0分

        # 2. 计算正分
        for pattern, points, is_required in config["patterns"]:
            if re.search(pattern, text):
                score += points
                if is_required:
                    must_have_matched = True

        # 3. 检查必须匹配的规则
        if not must_have_matched:
            return 0

        return min(score, self.MAX_SCORE)


rule_engine = RuleEngine()