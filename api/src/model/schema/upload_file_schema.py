from dataclasses import dataclass
from typing import Optional
from src.infra.sql_db.entity.upload_file_entity import UploadFileEntity
from src.infra.sql_db.entity.upload_file_chunk_entity import UploadFileChunkEntity

@dataclass
class UploadFileCreate:
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    file_type: str
    page_count: Optional[int] = None
    author: Optional[str] = None
    title: Optional[str] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None

    def to_entity(self):
        return UploadFileEntity(
            file_path=self.file_path,
            file_name=self.file_name,
            file_size=self.file_size,
            file_hash=self.file_hash,
            file_type=self.file_type,
            page_count=self.page_count,
            author=self.author,
            title=self.title,
            word_count=self.word_count,
            character_count=self.character_count,
        )


@dataclass
class UploadFileChunkCreate:
    content: str
    chunk_source: str
    parent_chunk_index: int
    child_chunk_index: Optional[int] = None
    page_number: Optional[int] = None
    page_name: Optional[str] = None
    section: Optional[str] = None

    def to_entity(self):
        return UploadFileChunkEntity(
            content=self.content,
            chunk_source=self.chunk_source,
            parent_chunk_index=self.parent_chunk_index,
            child_chunk_index=self.child_chunk_index,
            page_number=self.page_number,
            page_name=self.page_name,
            section=self.section,
        )

    def to_dict(self):
        return {
            "chunk_source": self.chunk_source,
            "parent_chunk_index": self.parent_chunk_index,
            "child_chunk_index": (
                self.child_chunk_index if self.child_chunk_index else -1
            ),
            "page_number": self.page_number if self.page_number else -1,
            "page_name": self.page_name if self.page_name else "",
            "section": self.section if self.section else "",
        }
