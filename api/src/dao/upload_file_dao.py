from src.infra.vector_store import VectorStore
from src.infra.sql_db.repo import upload_file_repo
from src.config.settings import setup_logging

logger = setup_logging()


class UploadFileDao:

    def __init__(self, store_name: str):

        self.upload_file_vector = VectorStore(store_name=store_name)

        self.upload_file_repo = upload_file_repo

    def save_upload_file(self, file, chunks):
        print("文件保存sql数据库中")
        self.upload_file_repo.save_upload_file(file, chunks)

    def add_vector_store_documents(self, docs: list):
        try:
            self.upload_file_vector.add_documents(docs)
        except Exception as e:
            logger.error(f"操作失败，原因是:{e}")

    def get_documents(self, user_input: str) -> list[dict]:
        return self.upload_file_vector.search(user_input)
