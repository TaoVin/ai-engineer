#__init__.py


from fastapi import APIRouter

from app.api.v1.endpoints.system import users, permission, roles

system_api_router = APIRouter()

# 用户路由
system_api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户"],
    responses={404: {"description": "未找到"}},
)
system_api_router.include_router(
    roles.router,
    prefix="/role",
    tags=["角色"],
    responses={404: {"description": "未找到"}},
)
system_api_router.include_router(
    permission.router,
    prefix="/permission",
    tags=["权限"],
    responses={404: {"description": "未找到"}},
)