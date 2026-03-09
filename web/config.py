"""
配置文件 - 定义常量、样式和配置参数
"""

# 颜色主题
THEME = {
    "primary": "#10a37f",  # DeepSeek 主题色
    "bg_primary": "#ffffff",
    "bg_secondary": "#f7f7f8",
    "text_primary": "#1a1a1a",
    "text_secondary": "#6b7280",
    "border": "#e5e7eb",
    "user_bubble": "#f3f4f6",
    "assistant_bubble": "#10a37f"
}

# 文件上传配置
ALLOWED_FILE_TYPES = [
    "txt", "pdf", "doc", "docx", 
    "xls", "xlsx", "ppt", "pptx",
    "jpg", "jpeg", "png", "gif",
    "mp3", "wav", "mp4", "avi",
    "py", "js", "java", "cpp", "c", "html", "css", "json"
]

MAX_FILE_SIZE_MB = 10

# 对话配置
MAX_CONVERSATIONS = 50
MESSAGE_HISTORY_LIMIT = 1000