"""
主应用程序
"""

import os
import gradio as gr
from typing import List, Tuple
from api_client import APIClient
import time
from components.sidebar import create_sidebar


# 定义截断函数
def truncate_text(text, max_len=12):
    """文字超过max_len显示..."""
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


class DeepSeekChatFrontend:
    def __init__(self):
        # 初始化API客户端
        self.api_client = APIClient()

        # 当前状态
        self.current_conversation_id = None
        self.current_user_input = None
        self.current_files = []

        self._create_interface()

    def _create_interface(self):
        """创建主界面"""

        css_content = self._load_css()

        with gr.Blocks(
            title="忆伴",
            theme=gr.themes.Soft(),
            css=css_content,
            fill_width=True,
        ) as self.interface:

            with gr.Row(elem_classes="gradio-container"):

                # 侧边栏
                with gr.Column(scale=1):
                    (
                        _,
                        new_chat_btn,
                        button_map,
                        self.conv_container,
                        load_conversations_func,
                        user_btn,
                    ) = create_sidebar(self.api_client)

                # 主界面
                with gr.Column(scale=5, elem_classes="main-container"):

                    # 标题栏
                    with gr.Row(elem_classes="head-container"):
                        self.conversation_title = gr.Markdown("## 新对话")

                    # 交互区
                    with gr.Row(elem_classes="body-container"):
                        chat_history = []
                        self.chatbot = gr.Chatbot(
                            height=760,
                            show_label=False,
                            value=chat_history,
                            show_copy_button=True,
                            avatar_images=(
                                "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                                "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
                            ),
                        )

                        with gr.Column(elem_classes="enter-bar"):
                            with gr.Row(elem_classes="enter-row"):
                                # 隐藏File组件
                                file_upload = gr.File(
                                    file_count="multiple",
                                    file_types=[
                                        "text",
                                        "image",
                                        "audio",
                                        "video",
                                        "pdf",
                                    ],
                                    visible=False,  # 完全隐藏
                                    elem_id="hidden-file-upload",
                                )

                                upload_btn = gr.Button(
                                    "📁 上传",
                                    variant="secondary",
                                    scale=1,
                                    elem_id="upload-button",
                                )

                                msg_input = gr.Textbox(
                                    show_label=False,
                                    placeholder="输入消息...",
                                    lines=3,
                                    scale=5,
                                    elem_id="message-input",
                                )

                                send_btn = gr.Button(
                                    "发送",
                                    variant="primary",
                                    scale=1,
                                    elem_id="send-button",
                                )

            # ========== 事件绑定 ==========

            # 新建对话
            new_chat_btn.click(
                fn=self._change_chat_window,
                inputs=None,
                outputs=[self.conversation_title, self.chatbot],
                queue=False,
            )

            for item in button_map:
                btn = item["btn"]
                btn.click(
                    fn=lambda cid=item["conv_id"]: self._change_chat_window(cid),
                    inputs=[],
                    outputs=[self.conversation_title, self.chatbot],
                    queue=False,
                )

            upload_btn.click(
                fn=None,  # 不需要Python函数
                inputs=None,
                outputs=None,
                js="""
                () => {
                    // 点击按钮时触发隐藏的文件输入
                    const fileInput = document.querySelector('#hidden-file-upload input[type="file"]');
                    if (fileInput) {
                        fileInput.click();
                    }
                    return [];
                }
                """,
            )

            # 发送消息
            send_btn.click(
                fn=self._handle_send_message,
                inputs=[msg_input, file_upload, self.chatbot],
                outputs=[self.chatbot, msg_input, file_upload]
            ).then(
                fn=self._get_ai_response,
                inputs=[self.chatbot],
                outputs=[self.chatbot]
            )

    def _load_css(self):
        """加载CSS文件"""
        css_file = "styles.css"

        # 如果CSS文件存在，读取内容
        if os.path.exists(css_file):
            with open(css_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            # 如果文件不存在，使用内联样式作为后备
            return """
            .gradio-container {
                height: 100vh !important;
                max-height: 100vh !important;
                overflow: hidden !important;
            }
            .chat-container {
                height: 100vh !important;
                display: flex !important;
                flex-direction: column !important;
            }
            #chatbot-container {
                flex: 1 !important;
                overflow-y: auto !important;
            }
            """

    # ========== API调用方法 ==========
    def _change_chat_window(self, conv_id: str = "") -> Tuple[str, List]:
        if not conv_id:
            return gr.Markdown("## 新对话"), []
        print(conv_id)
        self.current_conversation_id = conv_id

        conversation = self.api_client.get_conversation_detail(
            self.current_conversation_id
        )
        print(f"conversation:{conversation}")

        if conversation is None:
            return gr.Markdown("## 对话不存在，请刷新"), []

        title = conversation.get("title", "")
        messages = conversation.get("messages", [])

        chat_history = []
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                user_msg = messages[i]["content"]
                ai_msg = messages[i + 1]["content"]
            chat_history.append([user_msg, ai_msg])

        return gr.Markdown(f"## {title}"), chat_history

    def _handle_send_message(
        self, message: str, files: List, chat_history: List
    ) -> Tuple[List, str, List]:
        """处理用户发送消息"""

        print("=== 调试信息 ===")
        print(f"消息: '{message}'")
        print(f"文件对象: {files}")
        print(f"文件类型: {type(files)}")

        if not message and not files:
            return chat_history, message, files

        self.current_user_input = message

        # 处理文件
        file_info = []
        files_for_show = ""
        if files:
            self.current_files.clear()
            for f in files:
                file_info.append(
                    {
                        "name": f.name,
                        "type": f.name.split(".")[-1] if "." in f.name else "unknown",
                    }
                )
                print(f.name)
                print(type(f.name))
                self.current_files.append(f.name)

            print(file_info)
            files_for_show = "\n".join(
                [f"- {os.path.basename(f['name'])}" for f in file_info]
            )
            message += f"\n\n 附件:{files_for_show}"

        # 调用API创建对话
        if not chat_history:
            result = self.api_client.create_conversation(message)
            print(f"新id为:{result}")
            self.current_conversation_id = result

        chat_history.append(
            (message, None)
        )  # Chatbot组件期望的chat_history格式是：[一个元组 (用户消息, AI回复)]

        # 清空输入
        return (chat_history, "", [])

    def _get_ai_response(self, chat_history: List):
        """获取AI回复（流式）"""
        print("开始获取AI回复（流式）")
        if not chat_history or not self.current_conversation_id or chat_history[-1][1]:
            return chat_history

        # 初始化AI回复内容
        ai_message = ""

        # 调用流式API
        for chunk in self.api_client.chat_stream(
            self.current_conversation_id, self.current_user_input, self.current_files
        ):
            if chunk:
                ai_message += chunk
                print(f"流式输出:{chunk}")
                chat_history[-1] = (chat_history[-1][0], ai_message)
                yield chat_history

    def launch(self):
        """启动应用"""
        self.interface.launch(server_name="127.0.0.1", server_port=7860, share=False)


if __name__ == "__main__":
    app = DeepSeekChatFrontend()
    app.launch()
