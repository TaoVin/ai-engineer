"""角色控制器"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.base import PaginatedResponse, ResponseBase
from app.schemas.system.role import RoleBindPermissionDto, RoleCreate, RoleDto, RoleParam, RoleResponse
from app.service.system import get_role_service
from app.service.system.role_service import RoleService

router = APIRouter()


def _get_role_params(
    id: int = Query(0, description="主键ID"),
    role_name: str | None = Query(None, description="角色名称"),
    role_key: str | None = Query(None, description="角色键值"),
    description: str | None = Query(None, description="角色描述"),
    sort: int | None = Query(None, description="排序"),
) -> RoleParam:
    return RoleParam(
        id=id, role_name=role_name, role_key=role_key,
        description=description, sort=sort,
    )


# 增
@router.post(
    "/create", response_model=ResponseBase[RoleResponse], summary="角色创建"
)
async def create(
    data: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
):
    role = await role_service.create(db, obj_in=data.model_dump())
    return ResponseBase(
        data=RoleResponse.model_validate(role) if role else None
    )


# 删
@router.delete("/delete/{ids}", response_model=ResponseBase[bool])
async def delete(
    ids: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
):
    ids_list = list(map(int, ids.split(",")))
    await role_service.delete(db, ids=ids_list)
    return ResponseBase(data=True)


# 改
@router.post("/update", response_model=ResponseBase[bool])
async def update(
    db: Annotated[AsyncSession, Depends(get_db)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    dto: RoleDto,
):
    await role_service.update(db, obj_in=RoleDto.model_dump(dto))
    return ResponseBase(data=True)


# 查 - 分页
@router.get("/query/pages", response_model=PaginatedResponse[RoleResponse])
async def query_page(
    db: Annotated[AsyncSession, Depends(get_db)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    params: RoleParam = Depends(_get_role_params),
    page_num: int = 1,
    page_size: int = 10,
):
    return await role_service.query_by_page(db, params=params, page_num=page_num, page_size=page_size)


# 查 - 详情
@router.get("/query/{id}", response_model=ResponseBase[RoleResponse])
async def query_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
):
    role = await role_service.query_by_id(db, id=id)
    return ResponseBase(data=RoleResponse.model_validate(role) if role else None)



# 解绑权限
@router.delete("/unbindPermission/{id}", response_model=ResponseBase[bool], summary="角色解绑权限")
async def unbind_permission(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
):
    await role_service.unbind_permission(db, id=id)
    return ResponseBase(data=True)


# 绑定权限
@router.post("/bindPermission", response_model=ResponseBase[bool])
async def bindPermission(
    db: Annotated[AsyncSession, Depends(get_db)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    dto: RoleBindPermissionDto,
):
    await role_service.bindPermission(db, dto = dto)
    return ResponseBase(data=True)