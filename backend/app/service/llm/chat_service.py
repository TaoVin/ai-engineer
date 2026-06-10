"""用户服务"""

from typing import Any

from app.core.deps import get_db
from app.models.llm.chat import ChatMessage, ChatSession
from app.schemas.llm.chat import MessageItem, SessionInfo, SessionListParams
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper.llm.chat_mapper import chat_session_crud, chat_message_crud
from typing import Annotated
from fastapi.params import Depends
class ChatService:

    def __init__(self):
        pass

    async def get_chat_session(self, session_id: str, db:Annotated[AsyncSession, Depends(get_db)]) -> ChatSession | None:
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    
    async def query_sessions(self, db:Annotated[AsyncSession, Depends(get_db)], *, params: SessionListParams) -> list[ChatSession] | None:
        stamt = select(ChatSession)

        if not params.session_id and params.session_id != '':
           stamt = stamt.where(ChatSession.session_id == params.session_id)
        
        if not params.name and params.name != '':
           stamt = stamt.where(ChatSession.name.like(params.name))
        
        stamt = stamt.order_by(ChatSession.last_time.desc())    
        if not params.session_id and not params.name:
            stamt = stamt.limit(10)
        result = await db.execute(stamt)
        return list(result.scalars().all())

    async def update_session(self, session: SessionInfo, db:Annotated[AsyncSession, Depends(get_db)]) -> ChatSession:
        session_id = session.session_id
        if not session_id:
            raise ValueError("无效会话, 更新失败")
        chat_session = await self.get_chat_session(session_id=session_id, db = db)
        if not chat_session:
            return await chat_session_crud.create(db, obj_in=session.model_dump())
        session.id = chat_session.id
        return await chat_session_crud.update(db, db_obj= chat_session, obj_in=session.model_dump())
    
    async def save_message(self, message: MessageItem, db:Annotated[AsyncSession, Depends(get_db)]) -> ChatMessage:
       return await chat_message_crud.create(db=db, obj_in=message.model_dump())