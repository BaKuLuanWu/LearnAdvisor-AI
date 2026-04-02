# 🎓LearnAdvisor AI：忆伴
忆伴是一款基于RAG（检索增强生成）架构的知识增强型对话系统，专为技术学习者和职场新人打造。它以深度意图理解与个性化知识适配为核心，让每一次交互既精准落地，又懂你所需。

## 👆在线体验
HuggingFace：

## 🎬界面预览
占位

## 🎯功能特性
意图识别：三层递进架构（规则引擎 → 向量检索 → 大模型兜底），支持模糊意图二次识别（联网搜索增强）

RAG检索：基于ChromaDB + text-embedding-3，从课程知识库中召回最相关上下文，辅助生成精准回答

文件上传解析：支持PDF、Word、TXT、Excel等格式，自动提取文本、清洗、切块，存入PostgreSQL与向量库

上下文管理：默认5轮工作记忆；付费用户支持多级摘要（一级/二级）、关键语句提取与用户画像生成

意图引导与多轮对话路由：通过模板化询问收集缺失信息，栈结构保留旧意图上下文，支持平滑切换

问题推荐：基于意图分类、标签模板、推荐频率动态生成推荐问题，覆盖课程、专业、文档、闲聊、unknown等场景

系统性能优化：Redis缓存会话状态与最近5轮对话；异步处理模型API、数据库I/O；数据库联合索引加速摘要和消息查询

## 🏗️系统架构
```用户输入 → 意图识别(L1→L2→L3) → 路由引导/槽位填充 → RAG检索/文件解析 → 长程记忆注入 → LLM生成 → 推荐问题附加```

数据存储：PostgreSQL（文本块、元数据、摘要、用户画像）、ChromaDB（课程标题向量、关键语句向量）、Redis（会话缓存）

异步与缓存：线程池/协程处理耗时操作；LRU淘汰策略维持热点数据

外部依赖：大语言模型API（兼容OpenAI接口）、网络搜索插件、嵌入模型服务

## 💡核心难点
成本与准确性的平衡：纯 LLM 调用延迟高、费用贵。通过三层漏斗，规则层拦截约 60% 请求，L2 向量检索命中则无需调用模型，L3 仅用 3B 小模型兜底，整体 LLM 调用量大幅下降。

长对话记忆的渐进式压缩：通用模型对强指令摘要理解差，易忽略约束或话题偏斜。设计了精细提示词（分组识别相近意图、限制轮次、输出 JSON）+ 定时任务（每 5 轮一级摘要，每 15 条二级摘要），确保摘要可控；用户画像基于摘要与原始输入定期生成，避免信息失真。

文件解析依赖冲突：Unstructured 库依赖链复杂导致环境无法构建。改用 pdfplumber、python-docx 等轻量库按类型适配，牺牲统一性换取稳定性；后续计划拆分为独立微服务。

路由逻辑简单：当前基于规则，边缘场景覆盖有限。计划迭代为混合路由（80% 规则 + 20% 轻量模型动态判断），并积累数据优化规则库。

向量检索污染：个人历史意图库若存入模型错误结果会导致错误传播。当前仅依赖个人库 + 降级到模型兜底，后续需设计错误清洗与差分隐私方案。

## 🛠️技术栈
| 类别 | 技术 | 用途 |
|:-----|:-----|:-----|
| 编程语言 | Python 3.12.12 | 项目开发语言 |
| Web框架 | FastAPI | API服务端 |
| AI框架 | Langchain | LLM应用开发 |
| 嵌入模型 | text-embedding-3 | 知识向量化 |
| 大语言模型API | DashScope (阿里云) | 意图识别、摘要、回答生成 |
| 向量数据库 | ChromaDB | RAG检索与向量存储 |
| 关系型数据库 | PostgreSQL + SQLAlchemy | 存储文本块、摘要、用户画像 |
| 缓存中间件 | Redis | 会话状态缓存与工作记忆队列 |
| 文件解析 | pdfplumber / python-docx... | 多格式文本提取 |
| 原型工具 | Gradio | 快速原型展示/交互界面 |

## 📦项目结构
```
├── intent_recognition/
│   ├── rule_engine.py          # 正则+关键词权重匹配
│   ├── vector_retrieval.py     # 个人库/公共库向量检索
│   └── model_recognizer.py     # LLM兜底识别 + 联网搜索
├── rag/
│   ├── chroma_client.py        # 课程知识库向量化与检索
│   └── retriever.py            # top-k召回 + 上下文构造
├── file_upload/
│   ├── parser.py               # 根据扩展名调用解析器
│   ├── cleaner.py              # 编码统一、乱码过滤
│   └── chunker.py              # 语义切块 + 元数据关联
├── context_management/
│   ├── summary.py              # 一级/二级摘要定时任务
│   ├── key_sentence.py         # 关键句识别与存储
│   └── user_profile.py        # 画像生成（每日0点）
├── conversation_routing/
│   ├── router.py               # 多轮状态机 + 槽位填充
│   └── stack_context.py       # 旧意图栈管理
├── question_recommendation/
│   ├── intent_strategy.py      # 不同意图的模板/标签生成
│   └── frequency_controller.py # 推荐分数动态调整
├── performance/
│   ├── redis_cache.py          # 会话缓存 + 工作记忆队列
│   ├── async_tasks.py          # 异步模型/数据库调用
│   └── db_indexes.sql          # 联合索引创建语句
├── tests/                      # 功能测试（意图、RAG、文件上传等）
└── config_settings.py          # 日志、API密钥、超时阈值
```
## 🚀快速开始
环境准备：Python 3.9+，安装前后端依赖 pip install -r requirements.txt

数据库初始化：创建PostgreSQL数据库，执行 db_indexes.sql 建立索引；启动Redis服务

配置密钥：在 .env 中填写LLM API密钥（DeepSeek/阿里云DashScope等）

加载课程知识库：将CSV文件（含 course_title 字段）放入 data/，运行 rag/chroma_client.py 生成向量集合

启动服务：运行主程序（如 后端run.py 及 Gradio 界面）

测试：发送消息“我想学Python”，观察意图识别 → RAG检索 → 生成回答 → 推荐问题

## 🔮未来计划
- 统一解析服务：将Unstructured库部署为独立微服务，通过API调用，解决复杂文档解析
- 公共向量库：从个人库中聚合语义相近的高频问题-意图对（需解决隐私安全问题）
- 向量缓存：缓存语义完全相同的用户输入对应的回复结果
- 消息队列：引入RabbitMQ/Kafka处理跨服务耗时调用，提升吞吐
- 用户行为分析：离线分析历史对话，获取可挖掘细节，生成更个性化的问题推荐

## 📙开发文档
https://ccn6few6uwq2.feishu.cn/wiki/AZhPwNZiriH0uEk5HSZccfNtnpf?from=from_copylink
