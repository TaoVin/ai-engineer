"""用户控制器"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.base import PaginatedResponse, ResponseBase
from app.schemas.system.user import (
    UserBindRoleDto,
    UserCreate,
    UserDto,
    UserParam,
    UserResponse,
)
from app.service.system import get_user_service
from app.service.system.user_service import UserService

router = APIRouter()


def _get_user_params(
    id: int = Query(0, description="主键ID"),
    user_name: str | None = Query(None, description="登陆账号"),
    nick_name: str | None = Query(None, description="名字"),
    email: str | None = Query(None, description="邮箱"),
) -> UserParam:
    return UserParam(
        id=id, user_name=user_name, nick_name=nick_name, email=email,
    )


# 增
@router.post(
    "/create", response_model=ResponseBase[UserResponse], summary="用户创建"
)
async def create(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.create(db, obj_in=data.model_dump())
    return ResponseBase(
        data=UserResponse.model_validate(user) if user else None
    )


# 删
@router.delete("/delete/{ids}", response_model=ResponseBase[bool])
async def delete(
    ids: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    ids_list = list(map(int, ids.split(",")))
    await user_service.delete(db, ids=ids_list)
    return ResponseBase(data=True)


# 改
@router.post("/update", response_model=ResponseBase[bool])
async def update(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    dto: UserDto,
):
    await user_service.update(db, obj_in=UserDto.model_dump(dto))
    return ResponseBase(data=True)


# 查 - 分页
@router.get("/query/pages", response_model=PaginatedResponse[UserResponse])
async def query_page(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    params: UserParam = Depends(_get_user_params),
    page_num: int = 1,
    page_size: int = 10,
):
    return await user_service.query_by_page(db, params=params, page_num=page_num, page_size=page_size)


# 查 - 根据用户名（必须在 /query/{id} 之前定义）
@router.get("/query/byName", response_model=ResponseBase[UserResponse])
async def get_user_by_name(
    userName: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_by_username(db, username=userName)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)


# 查 - 详情
@router.get("/query/{id}", response_model=ResponseBase[UserResponse])
async def query_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.query_by_id(db, id=id)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)


# 绑定角色
@router.post("/bindRole", response_model=ResponseBase[bool], summary="用户绑定角色")
async def bind_role(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    dto: UserBindRoleDto,
):
    await user_service.bind_role(db, dto=dto)
    return ResponseBase(data=True)
