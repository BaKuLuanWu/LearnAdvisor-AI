"""
文件处理器 - 处理文件上传和预览
"""
import os
import tempfile
from typing import Optional
import gradio as gr

class FileProcessor:
    @staticmethod
    def is_allowed_file(filename: str, allowed_types: list) -> bool:
        """检查文件类型是否允许"""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        return ext in allowed_types
    
    @staticmethod
    def get_file_preview(file_path: str) -> Optional[str]:
        """获取文件预览内容"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.txt', '.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.json']:
                # 文本文件
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)  # 读取前1000个字符
                    return f"```{ext[1:]}\n{content}\n```"
            
            elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                # 图片文件
                return f"![图片]({file_path})"
            
            else:
                # 其他文件
                return f"📎 文件: {os.path.basename(file_path)}"
                
        except Exception as e:
            return f"❌ 无法预览文件: {str(e)}"
    
    @staticmethod
    def save_uploaded_file(file_obj) -> str:
        """保存上传的文件到临时目录"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_obj.name)
        
        # 如果是临时文件，直接使用
        if hasattr(file_obj, 'name'):
            return file_obj.name
        
        # 否则保存文件
        with open(file_path, 'wb') as f:
            if hasattr(file_obj, 'read'):
                f.write(file_obj.read())
            else:
                # Gradio 文件对象
                import shutil
                shutil.copy2(file_obj, file_path)
        
        return file_path