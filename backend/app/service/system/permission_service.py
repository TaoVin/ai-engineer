from tkinter.messagebox import NO
from typing import Any

from dulwich.lru_cache import V
from rich.pretty import d
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import BusinessError
from app.mapper.system.permission_mapper import permission_crud
from app.models.system.permission import Permission
from app.models.system.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.system.permission import PermissionDto, PermissionResponse

class PermissionService:
    
    def __init__(self):
        pass
    
    # 增
    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Permission:
        return await permission_crud.create(db, obj_in=obj_in)


    # 删除
    async def delete(self, db: AsyncSession, *, ids: list[int]):
        await permission_crud.remove_logic(db, ids=ids)
        
    # 查
    async def query_by_id(self, db: AsyncSession, *, id: int) -> Permission | None:
        return await permission_crud.get(db, id=int) 
    
    # 分页查
    async def query_by_page(self, db: AsyncSession, dto: PermissionDto, page_num: int = 1, page_size: int = 10) -> PaginatedResponse[PermissionResponse]:
        return await permission_crud.get_page(db, page_num = page_num, page_size = page_size, filters=dict(dto))
     

    
    # 改
    async def update(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Permission:
        id = obj_in['id']
        if id is None or id == 0:
            raise ValueError("无效id, 更新失败")
        permission = await self.query_by_id(db, id=int(str(id)))
        if permission is None:
            raise ValueError("无效id, 更新失败")
        return await permission_crud.update(db, db_obj=permission, obj_in=obj_in)