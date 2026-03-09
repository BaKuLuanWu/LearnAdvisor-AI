from ..entity.user_entity import UserEntity
from src.config import db_manager


class UserRepository:

    def __init__(self):
        pass

    def get_by_id(self, id: str):
        """根据用户id获取用户详情"""
        with db_manager.session_scope() as session:
            return session.query(UserEntity).filter(UserEntity.id == id).first()

    def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
    ):
        with db_manager.session_scope() as session:
            user = UserEntity(
                username=username, email=email.lower(), hashed_password=hashed_password
            )
            session.add(user)
            session.flush()
            print(f"用户创建成功: {user.username} (ID: {user.id})")
            return user.id


user_repo = UserRepository()