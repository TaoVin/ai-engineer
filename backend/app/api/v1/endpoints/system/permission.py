"""权限控制器"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.enums.system import PermissionType
from app.schemas.system.permission import PermissionDto, PermissionParam, PermissionResponse, PermissionCreate
from app.service.system import get_permission_service
from app.service.system.permission_service import PermissionService
from app.schemas.base import PaginatedResponse, ResponseBase

router = APIRouter()


def _get_permission_params(
    id: int = Query(0, description="主键ID"),
    permission_name: str | None = Query(None, description="权限名"),
    parent_id: int | None = Query(None, description="父级权限id"),
    permission_key: str | None = Query(None, description="权限标识"),
    permission_type: PermissionType | None = Query(None, description="权限类型"),
    path: str | None = Query(None, description="路由路径"),
) -> PermissionParam:
    return PermissionParam(
        id=id, permission_name=permission_name, parent_id=parent_id,
        permission_key=permission_key, permission_type=permission_type, path=path,
    )


# 增
@router.post(
    "/create", response_model=ResponseBase[PermissionResponse], summary="权限创建"
)
async def create(
    data: PermissionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
):
    permission = await permission_service.create(db, obj_in=data.model_dump())
    return ResponseBase(
        data=PermissionResponse.model_validate(permission) if permission else None
    )


# 删
@router.delete("/delete/{ids}", response_model=ResponseBase[bool])
async def delete(
    ids: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
):
    ids_list = list(map(int, ids.split(',')))
    await permission_service.delete(db, ids=ids_list)
    return ResponseBase(data=True)


# 改
@router.post("/update", response_model=ResponseBase[bool])
async def update(
    db: Annotated[AsyncSession, Depends(get_db)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    dto:PermissionDto  
):
    await permission_service.update(db, obj_in = PermissionDto.model_dump(dto))
    return ResponseBase(data=True)


# 查
@router.get("/query/pages", response_model=PaginatedResponse[PermissionResponse])
async def query_page(
    db: Annotated[AsyncSession, Depends(get_db)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    params: PermissionParam = Depends(_get_permission_params),
    page_num: int = 1, 
    page_size: int = 10
):
    return await permission_service.query_by_page(db, params=params, page_num=page_num, page_size=page_size)


@router.get("/query/{id}", response_model=ResponseBase[PermissionResponse])
async def query_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
):
    permission = await permission_service.query_by_id(db, id = id)
    return ResponseBase(data=PermissionResponse.model_validate(permission) if permission else None)
