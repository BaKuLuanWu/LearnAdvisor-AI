class UserDao:

    def __init__(self):
        pass

    def get_vip_members(self) -> set[str]:
        return {
            "user10086",
            "user1992",
            "user9897",
            "019bf364-e196-71cd-9522-e0f49d773f7d",
        }


user_dao = UserDao()
