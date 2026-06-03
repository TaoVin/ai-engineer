from typing import Any

from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDUser(CRUDBase[User]):
    """用户CRUD 操作"""

    # 增
    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> User:
        return await super().create(db, obj_in=obj_in)

    
    # 查 "*" 号后面的参数必须以key-value形式传参
    async def get_by_username(self, db: AsyncSession, *, username: str) -> User | None:
        """根据用户名获取用户"""
        result = await db.execute(
            select(User).where(User.user_name == username)
        )
        return result.scalar_one_or_none()

user_crud = CRUDUser(User)