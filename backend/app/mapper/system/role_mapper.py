from app.mapper.base import CRUDBase
from app.models.system.role import Role

class RoleMapper(CRUDBase[Role]):
    """角色CRUD 操作"""

role_crud = RoleMapper(Role)