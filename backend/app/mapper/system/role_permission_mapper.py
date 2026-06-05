

from app.mapper.base import CRUDBase
from app.models.system.association import RolePermission


class RolePermissionMapper(CRUDBase[RolePermission]):
    """用户CRUD 操作"""

role_permission_curd = RolePermissionMapper(RolePermission)