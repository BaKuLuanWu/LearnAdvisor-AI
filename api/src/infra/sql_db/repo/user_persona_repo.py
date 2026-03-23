from src.config import db_manager
from ..entity.user_persona_entity import UserPersonaEntity
from ..entity.summary_entity import SummaryEntity


class UserPersonaRepository:
    def __init__(self):
        pass

    def update_user_persona(self, conv_id, user_persona, start_index, end_index):
        with db_manager.session_scope() as session:
            entity = UserPersonaEntity(
                conversation_id=conv_id,
                user_role=user_persona.get("user_role"),
                major=user_persona.get("major"),
                grade=user_persona.get("grade"),
                learning_goal=user_persona.get("learning_goal"),
                current_courses=user_persona.get("current_courses"),
                knowledge_interests=user_persona.get("knowledge_interests"),
                question_types=user_persona.get("question_types"),
                file_analysis_preference=user_persona.get("file_analysis_preference"),
                reply_style_preference=user_persona.get("reply_style_preference"),
                knowledge_level=user_persona.get("knowledge_level"),
                topic_preferences=user_persona.get("topic_preferences"),
                dislikes=user_persona.get("dislikes"),
            )
            session.add(entity)
            session.query(SummaryEntity).filter(
                SummaryEntity.conversation_id == conv_id,
                SummaryEntity.compress_times == 2,
                SummaryEntity.start_index >= start_index,
                SummaryEntity.end_index <= end_index,
            ).update({SummaryEntity.is_active: False}, synchronize_session=False)


user_persona_repo = UserPersonaRepository()