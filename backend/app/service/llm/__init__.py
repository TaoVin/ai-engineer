"""系统管理服务"""

from typing import AsyncGenerator

from app.service.llm.chat_service import ChatService


async def get_chat_service() -> AsyncGenerator[ChatService, None]:
    """获取聊天服务实例"""
    yield ChatService()