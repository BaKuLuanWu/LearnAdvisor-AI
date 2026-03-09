import os
import pickle
import logging

logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
from src.config import setup_logging, vector_store_config
from typing import List, Dict, Optional, Any
from datetime import datetime
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
import chromadb
from chromadb.utils import embedding_functions
from chromadb import Documents, EmbeddingFunction, Embeddings
import numpy as np
import pandas as pd


logger = setup_logging()


class DashScopeEmbeddingWrapper(EmbeddingFunction):
    """DashScope 嵌入模型的 ChromaDB 适配器"""

    def __init__(self, api_key: str):

        self.model = DashScopeEmbeddings(
            model="text-embedding-v3", dashscope_api_key=api_key
        )

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.model.embed_documents(input)
        result = []
        for emb in embeddings:
            if isinstance(emb, np.ndarray):
                result.append(emb.tolist())
            else:
                result.append(emb)
        return result


class VectorStore:
    def __init__(self, store_name: str, config=None, data_source: str = None):
        self.store_name = store_name
        self.config = config or vector_store_config
        self.data_source = data_source  # 数据源路径参数

        # 设置存储路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.storage_path = os.path.join(script_dir, "chroma_db")

        # 确保存储目录存在
        os.makedirs(self.storage_path, exist_ok=True)

        api_key = os.getenv("DASHSCOPE_API_KEY")
        self.embedding_function = DashScopeEmbeddingWrapper(api_key)
        test_emb = self.embedding_function(["test"])
        self.embedding_dim = len(test_emb[0])
        print(f"Embedding维度: {self.embedding_dim}")

        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=self.storage_path)

        try:
            # 尝试获取已存在的集合
            self.collection = self.client.get_collection(
                name=store_name, embedding_function=self.embedding_function
            )

            print(f"{getattr(self.collection, 'id', None)}")

            print(
                f"✅ 已加载ChromaDB集合 '{store_name}'，包含 {self.collection.count()} 个文档"
            )
        except Exception as e:
            # 如果集合不存在，创建新的
            print(f"📭 未找到集合 '{store_name}'，创建新集合: {e}")
            self.collection = self.client.create_collection(
                name=store_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
            )

        print(f"数据源:{data_source}")

        if data_source != None:
            data_source_path = (
                os.path.dirname(os.path.abspath(__file__)) + "\\" + self.data_source
            )
        # 如果索引为空且有数据源，则自动导入
        if (
            self.collection.count() == 0
            and self.data_source
            and os.path.exists(data_source_path)
        ):
            print(f"检测到空向量库，正在从数据源导入: {self.data_source}")
            self._import_from_dataframe(data_source_path)

    def _import_from_dataframe(self, path: str):
        """从CSV数据源导入课程数据"""
        try:
            print(path)

            # 读取CSV文件
            df = pd.read_csv(path)
            print(f"成功读取 {len(df)} 条课程数据")

            # 创建课程文档
            course_documents = self._create_course_documents(df)

            # 添加到向量库
            if course_documents:
                self.add_documents(course_documents)
                print(f"✅ 成功导入 {len(course_documents)} 个课程文档")

        except Exception as e:
            print(f"导入数据失败: {e}")

    def _create_course_documents(self, df: pd.DataFrame) -> List[Document]:
        """创建课程文档列表"""
        documents = []

        for idx, row in df.iterrows():

            # 创建Document对象
            doc = Document(
                page_content=str(row.get("course_title", "")),
                metadata={
                    "organization": str(row.get("course_organization", "")),
                    "certificate_type": str(row.get("course_Certificate_type", "")),
                    "rating": float(row.get("course_rating", 0)),
                    "difficulty": str(row.get("course_difficulty", "Mixed")),
                    "students": str(row.get("course_students_enrolled", "")),
                    "difficulty_level": {
                        "Beginner": 1,
                        "Mixed": 2,
                        "Intermediate": 3,
                        "Advanced": 4,
                    }.get(str(row.get("course_difficulty", "Mixed")), 2),
                    "row_index": idx,
                    "source": "course_csv",
                    "import_time": datetime.now().isoformat(),
                },
            )
            documents.append(doc)

        print(f"✅ 已创建 {len(documents)} 门课程的描述")
        return documents

    def add_documents(self, documents: List[Document], batch_size: int = 10):
        """添加文档到向量存储"""
        if not documents:
            logger.warning("没有文档可添加")
            return

        logger.info(f"正在添加 {len(documents)} 个文档到ChromaDB...")

        try:
            # 分批处理
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]

                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                ids = [
                    f"doc_{i}_{datetime.now().timestamp()}_{j}"
                    for j in range(len(batch))
                ]

                # 添加当前批次
                self.collection.add(documents=texts, metadatas=metadatas, ids=ids)

                logger.info(
                    f"已添加批次 {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}: {len(batch)} 个文档"
                )

            logger.info(f"成功添加 {len(documents)} 个文档到 {self.store_name}")

        except Exception as e:
            logger.error(f"添加文档到ChromaDB失败: {e}")
            raise

    def search(
        self, query: str, k: int = 5, filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        try:
            # 构建查询
            where = {}
            if filter_dict:
                # 转换filter_dict为ChromaDB的where条件
                for key, value in filter_dict.items():
                    if isinstance(value, (list, tuple)):
                        where[key] = {"$in": value}
                    else:
                        where[key] = value

            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=where if where else None,
                include=["documents", "metadatas", "distances"],
            )

            # 格式化结果
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(
                    zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0],
                    )
                ):
                    formatted_results.append(
                        {
                            "content": doc,
                            "metadata": metadata,
                            "distance": distance,
                            "score": (
                                1 - distance if distance <= 1 else 1 / (1 + distance)
                            ),  # 转换为相似度分数
                        }
                    )

            return formatted_results

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """带分数的相似度搜索（兼容LangChain接口）"""
        results = self.search(query, k)
        return [
            (Document(page_content=r["content"], metadata=r["metadata"]), r["score"])
            for r in results
        ]

    def get_all_documents(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """获取所有文档"""
        try:
            results = self.collection.get(limit=limit)
            documents = []
            for i in range(len(results["ids"])):
                documents.append(
                    {
                        "id": results["ids"][i],
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i],
                    }
                )
            return documents
        except Exception as e:
            logger.error(f"获取所有文档失败: {e}")
            return []

    def update_document(self, doc_id: str, document: Document):
        """更新文档"""
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[document.page_content],
                metadatas=[document.metadata],
            )
            logger.info(f"文档 {doc_id} 更新成功")
        except Exception as e:
            logger.error(f"更新文档失败: {e}")

    def delete_document(self, doc_id: str):
        """删除文档"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"文档 {doc_id} 删除成功")
        except Exception as e:
            logger.error(f"删除文档失败: {e}")

    def get_stats(self) -> Dict:
        """获取向量存储统计信息"""
        try:
            count = self.collection.count()
            return {
                "store_name": self.store_name,
                "document_count": count,
                "vector_dimension": self.embedding_dim,
                "storage_path": self.storage_path,
                "collection_name": self.collection.name,
                "embedding_model": "DashScope text-embedding-v3",
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

    def clear(self):
        """清空向量存储"""
        try:
            # 删除整个集合
            self.client.delete_collection(self.store_name)
            # 重新创建空集合
            self.collection = self.client.create_collection(
                name=self.store_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"清空向量存储: {self.store_name}")
        except Exception as e:
            logger.error(f"清空向量存储失败: {e}")


# 创建全局单例
course_vector_store = VectorStore(store_name="course", data_source="course.csv")
intent_vector_store = VectorStore(store_name="intent")
title_vector_store = VectorStore(store_name="title")
