"""权限控制器"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.system.permission import PermissionDto, PermissionResponse
from app.service.system import get_permission_service
from app.service.system.permission_service import PermissionService
from app.schemas.base import ResponseBase
from app.schemas.system.user import UserResponse

router = APIRouter()


# 增
@router.post(
    "/create", response_model=ResponseBase[PermissionResponse], summary="权限创建"
)
async def create(
    data: PermissionDto,
    db: Annotated[AsyncSession, Depends(get_db)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
):
    permission = await permission_service.create(db, obj_in=data.model_dump())
    return ResponseBase(
        data=PermissionResponse.model_validate(permission) if permission else None
    )


# 删
@router.delete("/delete/{id}", response_model=ResponseBase[bool])
async def delete(
    ids: list[int],
    db: Annotated[AsyncSession, Depends(get_db)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
):
    await permission_service(db, username=userName)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)


# 改
@router.get("/query/byName", response_model=ResponseBase[UserResponse])
async def update(
    userName: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_by_username(db, username=userName)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)


# 查
@router.get("/query/byName", response_model=ResponseBase[UserResponse])
async def query_page(
    userName: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_by_username(db, username=userName)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)


@router.get("/query/{id}", response_model=ResponseBase[UserResponse])
async def query_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_by_username(db, username=userName)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)
