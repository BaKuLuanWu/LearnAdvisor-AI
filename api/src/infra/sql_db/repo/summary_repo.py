from src.config import db_manager
from sqlalchemy.sql import func
from ..entity.summary_entity import SummaryEntity


class SummaryRepository:
    def __init__(self):
        pass

    def get_recent_summary(self, conv_id: str):
        with db_manager.session_scope() as session:
            entity = (
                session.query(SummaryEntity)
                .filter(SummaryEntity.conversation_id == conv_id)
                .order_by(SummaryEntity.end_index.desc())
                .first()
            )
            return entity

    def get_recent_summary_level1_end_index(self, conv_id: str):
        with db_manager.session_scope() as session:
            return (
                session.query(func.max(SummaryEntity.end_index))
                .filter(
                    SummaryEntity.conversation_id == conv_id,
                    SummaryEntity.compress_times == 1,
                    SummaryEntity.is_active == True,
                )
                .scalar()
                or 0
            )

    def get_recent_summary_level2_end_index(self, conv_id: str):
        with db_manager.session_scope() as session:
            return (
                session.query(func.max(SummaryEntity.end_index))
                .filter(
                    SummaryEntity.conversation_id == conv_id,
                    SummaryEntity.compress_times == 2,
                    SummaryEntity.is_active == True,
                )
                .scalar()
                or 0
            )

    def add_summaries(self, entity_list: list[SummaryEntity]):
        with db_manager.session_scope() as session:
            session.add_all(entity_list)

    def add_lv2_summaries(
        self, entity_list: list[SummaryEntity], conv_id, start_index, end_index
    ):
        with db_manager.session_scope() as session:
            session.add_all(entity_list)
            session.query(SummaryEntity).filter(
                SummaryEntity.conversation_id == conv_id,
                SummaryEntity.start_index >= start_index,
                SummaryEntity.end_index <= end_index,
            ).update(
                {SummaryEntity.is_active: False}, synchronize_session=False
            )  # 不用更新session，提高性能

    def active_summary(self, conv_id, start_index, end_index):
        with db_manager.session_scope() as session:
            session.query(SummaryEntity).filter(
                SummaryEntity.conversation_id == conv_id,
                SummaryEntity.start_index >= start_index,
                SummaryEntity.end_index <= end_index,
            ).update({SummaryEntity.is_active: True}, synchronize_session=False)

    def get_summary_level1_list(self, conv_id: str):
        with db_manager.session_scope() as session:
            return (
                session.query(SummaryEntity)
                .filter(
                    SummaryEntity.conversation_id == conv_id,
                    SummaryEntity.compress_times == 1,
                    SummaryEntity.is_active == True,
                )
                .order_by(SummaryEntity.start_index)
                .all()
            )


summary_repo = SummaryRepository()
