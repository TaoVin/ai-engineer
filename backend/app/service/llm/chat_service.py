"""用户服务"""

from typing import Any

from app.core.deps import get_db
from app.models.llm.chat import ChatMessage, ChatSession
from app.schemas.llm.chat import MessageItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper.llm.chat_mapper import chat_session_crud, chat_message_crud
from typing import Annotated
from fastapi.params import Depends
class ChatService:

    def __init__(self):
        pass

    async def get_chat_session(self, session_id: str, db:Annotated[AsyncSession, Depends(get_db)]) -> ChatSession:
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_session(self, session: ChatSession, db:Annotated[AsyncSession, Depends(get_db)]) -> ChatSession:
        return await chat_session_crud.update(db, session.model_dump())
    
    async def save_message(self, message: MessageItem, db:Annotated[AsyncSession, Depends(get_db)]) -> ChatMessage:
       return await chat_message_crud.create(db=db, obj_in=message.model_dump())