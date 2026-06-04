
from fastapi import APIRouter

from app.api.v1.endpoints.system import users

api_router = APIRouter()
# 用户路由
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户"],
    responses={404: {"description": "未找到"}},
)