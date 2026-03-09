from src.config import db_manager
from sqlalchemy.sql import func
from ..entity.hot_question_entity import HotQuestionEntity


class HotQuestionRepository:

    def __init__(self):
        pass

    def get_hot_questions(self, quantity: int):
        with db_manager.session_scope() as session:
            result = (
                session.query(HotQuestionEntity)
                .order_by(HotQuestionEntity.click_times.desc())
                .limit(quantity)
                .all()
            )

            return result

    def add_hot_questions(self,questions:list):
        with db_manager.session_scope() as session:
            entity_list = []
            for q in questions:
                entity = HotQuestionEntity(content =q['content'],click_times=q['click_times'])
                entity_list.append(entity)
            session.add_all(entity_list)

hot_question_repo = HotQuestionRepository()