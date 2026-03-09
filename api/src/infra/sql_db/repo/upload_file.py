from src.model.schema.upload_file_schema import UploadFileCreate, UploadFileChunkCreate
from typing import List, Dict, Any, Optional
from src.config import db_manager


class UploadFileRepository:

    def __init__(self):
        pass

    def save_upload_file(
        self, file: UploadFileCreate, chunks: List[UploadFileChunkCreate]
    ):
        with db_manager.session_scope() as session:
            file_entity = file.to_entity()
            session.add(file_entity)
            session.flush()

            chunk_entity_list = []
            for chunk in chunks:
                chunk_entity = chunk.to_entity()
                chunk_entity.upload_file_id = file_entity.id
                chunk_entity_list.append(chunk_entity)
            session.add_all(chunk_entity_list)

            print(
                f"文件保存成功！文件名:{file_entity.file_name} 切块数量:{len(chunk_entity_list)}"
            )


upload_file_repo = UploadFileRepository()
