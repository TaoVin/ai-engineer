from app.mapper.base import CRUDBase
from app.models.system.association import UserRole


class UserRoleMapper(CRUDBase[UserRole]):
    """用户CRUD 操作"""

user_role_crud = UserRoleMapper(UserRole)