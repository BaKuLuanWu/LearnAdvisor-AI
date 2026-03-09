"""
文件上传组件 - 处理文件上传逻辑
"""
import gradio as gr
from typing import List
import config
from utils import FileProcessor

class FileUploadHandler:
    def __init__(self):
        self.current_files = []
        self.file_processor = FileProcessor()
    
    def handle_file_upload(self, files: List) -> tuple:
        """处理文件上传"""
        if not files:
            return [], gr.update(visible=False)
        
        valid_files = []
        for file in files:
            if self.file_processor.is_allowed_file(file.name, config.ALLOWED_FILE_TYPES):
                valid_files.append(file)
            else:
                print(f"不支持的文件类型: {file.name}")
        
        self.current_files = valid_files
        
        # 更新显示
        if valid_files:
            return valid_files, gr.update(
                value=valid_files,
                visible=True,
                label=f"已上传文件 ({len(valid_files)}个)"
            )
        else:
            return [], gr.update(visible=False)
    
    def get_file_previews(self, files: List) -> str:
        """获取文件预览文本"""
        previews = []
        for file in files:
            preview = self.file_processor.get_file_preview(file)
            if preview:
                previews.append(preview)
        
        if previews:
            return "\n\n".join(previews)
        return ""
    
    def clear_files(self):
        """清空文件"""
        self.current_files = []
        return [], gr.update(visible=False)