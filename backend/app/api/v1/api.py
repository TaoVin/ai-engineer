
from fastapi import APIRouter

from app.api.v1.endpoints.system import system_api_router

api_router = APIRouter()

# 用户路由
api_router.include_router(
    system_api_router,
    prefix="/sys",
    tags=["系统管理"],
    responses={404: {"description": "未找到"}},
)