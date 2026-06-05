

from app.mapper.base import CRUDBase
from app.models.system.permission import Permission


class PermissionMapper(CRUDBase[Permission]):
    """权限CRUD 操作"""

permission_crud = PermissionMapper(Permission)