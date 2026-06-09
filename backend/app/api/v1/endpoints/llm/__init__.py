#__init__.py


from fastapi import APIRouter

from app.api.v1.endpoints.llm import chat

chat_api_router = APIRouter()

# 用户路由
chat_api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["聊天"],
    responses={404: {"description": "未找到"}},
)