

from app.mapper.base import CRUDBase
from app.models.system.user import User


class UserMapper(CRUDBase[User]):
    """用户CRUD 操作"""

user_crud = UserMapper(User)