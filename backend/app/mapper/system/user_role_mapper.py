from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper.base import CRUDBase
from app.models.system.association import UserRole


class UserRoleMapper(CRUDBase[UserRole]):
    """用户角色关联CRUD 操作"""

    async def query_by_user_id(self, db: AsyncSession, user_id: int) -> Sequence[UserRole]:
        query = select(self.model).where(self.model.user_id == user_id).order_by(self.model.id)
        result = await db.execute(query)
        return result.scalars().all()


user_role_crud = UserRoleMapper(UserRole)
