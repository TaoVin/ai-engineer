"""角色服务"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper.system import role_permission_mapper
from app.mapper.system.role_mapper import role_crud
from app.mapper.system.role_permission_mapper import role_permission_curd
from app.models.system.association import RolePermission
from app.models.system.role import Role
from app.schemas.base import PaginatedResponse
from app.schemas.system.role import RoleBindPermissionDto, RoleParam, RoleResponse


class RoleService:

    def __init__(self):
        pass

    # 增
    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Role:
        return await role_crud.create(db, obj_in=obj_in)

    # 删
    async def delete(self, db: AsyncSession, *, ids: list[int]):
        await role_crud.remove_logic(db, ids=ids)

    # 查
    async def query_by_id(self, db: AsyncSession, *, id: int) -> Role | None:
        return await role_crud.get(db, id=id)

    # 分页查
    async def query_by_page(
        self, db: AsyncSession, params: RoleParam, page_num: int = 1, page_size: int = 10
    ) -> PaginatedResponse[RoleResponse]:
        return await role_crud.get_page(
            db, page_num=page_num, page_size=page_size,
            filters=dict(params), schema=RoleResponse
        )

    # 改
    async def update(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Role:
        id = obj_in["id"]
        if id is None or id == 0:
            raise ValueError("无效id, 更新失败")
        role = await self.query_by_id(db, id=int(str(id)))
        if role is None:
            raise ValueError("无效id, 更新失败")
        return await role_crud.update(db, db_obj=role, obj_in=obj_in)
    
    
    # 解绑权限
    async def unbind_permission(self, db: AsyncSession, *, id: int) -> None:
        await role_permission_curd.remove(db, id=id)


    async def bindPermission(
        self, db: AsyncSession, *, dto: RoleBindPermissionDto,
    ) -> None:
      role = await self.query_by_id(db, id = dto.id)
      if role is None:
          raise ValueError("无效的角色信息")
    
      bind_info_list = await role_permission_curd.query_by_role_id(db, role_id = role.id)
      
      # 存在已经绑定的关系，先全部删除，减少判断
      if bind_info_list is not None and len(bind_info_list) != 0:
        has_bind_permission_ids = [role_per.id for role_per in bind_info_list]
        # 删除所有
        await role_permission_curd.remove_batch(db, ids = has_bind_permission_ids)
    
      # 重新绑定
      if dto.permission_ids and len(dto.permission_ids) > 0:
            bind: list[RolePermission] = [RolePermission(role_id = role.id, permission_id=pId) for pId in dto.permission_ids]
            await role_permission_curd.create_batch(db, obj_in=bind)
      
        