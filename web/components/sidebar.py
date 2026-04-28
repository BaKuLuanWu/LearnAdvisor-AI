"""
侧边栏组件 - 调用API获取对话历史
"""

import gradio as gr
from api_client import APIClient


# 定义截断函数
def truncate_text(text, max_len=12):
    """文字超过max_len显示..."""
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def create_sidebar(api_client:APIClient):
    """创建侧边栏"""

    def load_conversations(api_client:APIClient):
        """加载对话历史"""
        print("加载历史对话")

        groups = api_client.get_grouped_conversations()

        if not groups:
            groups = {}

        ui_elements = []
        button_map = []

        for group_name, conv_list in groups.items():
            if conv_list:  # 如果列表不为空
                print('列表不为空')
                if group_name == "today":
                    title = "今天"
                elif group_name == "yesterday":
                    title = "昨天"
                elif group_name == "last7days":
                    title = "7天内"
                else:
                    title = "更早"

                ui_elements.append(
                    gr.HTML(
                        f"<h4 style='margin-left: 16px;color: rgb(138, 142, 149); font-weight: 600;'>{title}</h4>"
                    )
                )
                for conv in conv_list:
                    print(conv['title'])
                    row = gr.Row()
                    with row:
                        btn = gr.Button(
                            truncate_text(conv["title"], 12),
                            variant="secondary",
                            elem_id="old-chat-button",
                        )
                    ui_elements.append(row)
                    button_map.append({"btn": btn, "conv_id": conv["conv_id"]})

        return ui_elements, button_map

    with gr.Column(scale=1, min_width=250, elem_classes="sidebar-container") as sidebar:

        gr.Markdown("# 🐋 忆伴", elem_classes="sidebar-title")

        # 新建对话按钮
        new_chat_btn = gr.Button(
            "💬 新对话", variant="primary", elem_id="new-chat-button"
        )

        # 动态加载对话列表
        conv_container = gr.Column(elem_classes="conversation_container")

        with conv_container:
            _, button_map = load_conversations(api_client)

        with gr.Row(elem_classes="user_button_container"):
            user_number = 12214

            user_btn = gr.Button(
                f"👤 {user_number}", variant="secondary", elem_id="user_button"
            )

    return (
        sidebar,
        new_chat_btn,
        button_map,
        conv_container,
        load_conversations,
        user_btn,
    )
