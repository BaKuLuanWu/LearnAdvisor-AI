"""
聊天窗口组件 - 主聊天界面
"""
import gradio as gr
import markdown
import config
from datetime import datetime

def create_chat_window():
    """创建聊天窗口"""
    with gr.Column(scale=3, min_width=500) as chat_window:
        # 聊天标题
        chat_title = gr.Markdown(
            "# 新对话",
            elem_id="chat-title"
        )
        
        # 聊天消息容器
        chatbot = gr.Chatbot(
            label="",
            height=600,
            avatar_images=(
                "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",  # 用户头像
                "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"   # AI头像
            ),
            show_label=False,
            bubble_full_width=False,
            show_copy_button=True,
            render_markdown=True
        )
        
        # 输入区域
        with gr.Row():
            with gr.Column(scale=4):
                # 文件上传按钮
                file_btn = gr.UploadButton(
                    "📎 上传文件",
                    file_types=config.ALLOWED_FILE_TYPES,
                    file_count="multiple"
                )
                
                # 消息输入框
                msg = gr.Textbox(
                    placeholder="输入消息...",
                    show_label=False,
                    lines=2,
                    max_lines=5,
                    container=False
                )
            
            with gr.Column(scale=1, min_width=80):
                # 发送按钮
                send_btn = gr.Button(
                    "发送",
                    variant="primary",
                    size="lg"
                )
        
        # 已上传文件显示
        uploaded_files = gr.File(
            label="已上传文件",
            file_count="multiple",
            interactive=False,
            visible=False
        )
    
    return {
        "chat_window": chat_window,
        "chat_title": chat_title,
        "chatbot": chatbot,
        "msg": msg,
        "send_btn": send_btn,
        "file_btn": file_btn,
        "uploaded_files": uploaded_files
    }