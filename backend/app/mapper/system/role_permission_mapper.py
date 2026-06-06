

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper.base import CRUDBase
from app.models.system.association import RolePermission


class RolePermissionMapper(CRUDBase[RolePermission]):
    """角色权限关联CRUD 操作"""

    async def query_by_role_id(self, db: AsyncSession, role_id: int) -> Sequence[RolePermission]:
        query = select(self.model).where(self.model.role_id == role_id).order_by(self.model.id)
        result = await db.execute(query)
        return result.scalars().all()
        
        
        
role_permission_curd = RolePermissionMapper(RolePermission)