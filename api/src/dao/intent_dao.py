from src.infra.vector_store import intent_vector_store,VectorStore
from langchain_core.documents import Document
from datetime import datetime


class IntentDao:

    def __init__(self):
        self.intent_vector_store = intent_vector_store
        self.pending_intent_vector_store = VectorStore('pending_intent')

    def vector_search(self, query: str, k: int = 3):
        return self.intent_vector_store.search(query, k)

    def add_query_and_pending_intent_vector(self, query: str, intent: str):
        print('正在添加意图识别结果存储...')
        doc = Document(
            page_content=query,
            metadata={
                "intent": intent,
                "source": "program_output",
                "import_time": datetime.now().isoformat(),
            },
        )
        self.pending_intent_vector_store.add_documents([doc])
        print('意图识别结果添加成功!')


intent_dao = IntentDao()
