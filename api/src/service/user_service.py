from src.dao import user_dao


class UserService:

    def __init__(self):

        self.user_dao = user_dao

    def is_vip(self, user_id) -> bool:
        vip_members = self.user_dao.get_vip_members()

        if user_id in vip_members:
            return True

        return False


user_service = UserService()
