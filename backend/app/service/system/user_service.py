"""用户服务"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper.system.user_mapper import user_crud
from app.mapper.system.user_role_mapper import user_role_crud
from app.models.system.association import UserRole
from app.models.system.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.system.user import UserBindRoleDto, UserParam, UserResponse


class UserService:

    def __init__(self):
        pass

    # 增
    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> User:
        return await user_crud.create(db, obj_in=obj_in)

    # 删
    async def delete(self, db: AsyncSession, *, ids: list[int]):
        await user_crud.remove_logic(db, ids=ids)

    # 查
    async def query_by_id(self, db: AsyncSession, *, id: int) -> User | None:
        return await user_crud.get(db, id=id)

    # 根据用户名查询
    async def get_by_username(self, db: AsyncSession, *, username: str) -> User | None:
        result = await db.execute(
            select(User).where(User.user_name == username)
        )
        return result.scalar_one_or_none()

    # 分页查
    async def query_by_page(
        self, db: AsyncSession, params: UserParam, page_num: int = 1, page_size: int = 10
    ) -> PaginatedResponse[UserResponse]:
        return await user_crud.get_page(
            db, page_num=page_num, page_size=page_size,
            filters=dict(params), schema=UserResponse
        )

    # 改
    async def update(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> User:
        id = obj_in["id"]
        if id is None or id == 0:
            raise ValueError("无效id, 更新失败")
        user = await self.query_by_id(db, id=int(str(id)))
        if user is None:
            raise ValueError("无效id, 更新失败")
        return await user_crud.update(db, db_obj=user, obj_in=obj_in)

    # 解绑角色
    async def unbind_role(self, db: AsyncSession, *, id: int) -> None:
        await user_role_crud.remove(db, id=id)

    # 绑定角色
    async def bind_role(self, db: AsyncSession, *, dto: UserBindRoleDto) -> None:
        user = await self.query_by_id(db, id=dto.id)
        if user is None:
            raise ValueError("无效的用户信息")

        bind_info_list = await user_role_crud.query_by_user_id(db, user_id=user.id)

        # 存在已经绑定的关系，先全部删除，再重新绑定
        if bind_info_list is not None and len(bind_info_list) != 0:
            has_bind_ids = [ur.id for ur in bind_info_list]
            await user_role_crud.remove_batch(db, ids=has_bind_ids)

        # 重新绑定
        if dto.role_ids and len(dto.role_ids) > 0:
            bind: list[UserRole] = [
                UserRole(user_id=user.id, role_id=role_id) for role_id in dto.role_ids
            ]
            await user_role_crud.create_batch(db, obj_in=bind)
