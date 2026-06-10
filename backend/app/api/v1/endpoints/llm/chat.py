
import json
from datetime import datetime
from typing import Annotated

from pytest import param

from app.core.deps import get_db
from app.enums.llm import MessageRole
from app.models.llm.chat import ChatMessage, ChatSession
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from openai import AsyncOpenAI
from sse_starlette import EventSourceResponse

from app.core.openai import get_client, stream_ai_response
from app.core.redis import redis_manager
from app.schemas.base import PaginatedResponse, ResponseBase
from app.schemas.llm.chat import (
    ChatRequest,
    MessageItem,
    RenameRequest,
    SessionDetail,
    SessionInfo,
    SessionListParams,
)
from app.service.llm import get_chat_service
from app.service.llm.chat_service import ChatService
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter()



# ──────────────────────── 流式聊天 ────────────────────────

@router.post("/stream", summary="流式聊天")
async def chat_stream(
    chat_req: ChatRequest,
    client: Annotated[AsyncOpenAI, Depends(get_client)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    session_id = chat_req.session_id
    user_message = chat_req.message

    # 获取session
    session =await chat_service.get_chat_session(session_id, db)
    messags = []
    if not session:
        session = ChatSession(name = user_message[0: 10], session_id = session_id, last_time=datetime.now())
    else: 
        if session.messages:
           messags = [MessageItem.model_validate(msg, from_attributes=True) for msg in session.messages]


    session.last_time = datetime.now()
    session_info = SessionInfo.model_validate(session)
    session = await chat_service.update_session(session_info, db)
    
    # 创建当前记录
    current_message = MessageItem(role = MessageRole.USER, content = user_message, session_id = session_id)
    await chat_service.save_message(current_message, db)
    messags.append(current_message)

    async def event_generator():
        full_response = ""
        async for data in stream_ai_response(messags, client):
            yield f"data: {data}\n\n"

            obj = json.loads(data)
            if obj.get("type") == "token":
                full_response += obj["content"]
            elif obj.get("type") == "done":
                call_back_message = MessageItem(role = MessageRole.ASSISTANT, content = full_response, session_id = session_id)
                await chat_service.save_message(call_back_message, db)
            elif obj.get("type") == "error":
                print(f"Stream error: {obj['content']}")

    return EventSourceResponse(event_generator())


# ──────────────────────── 会话列表 ────────────────────────

@router.post("/sessions", summary="获取会话列表", description="默认取最后活跃的前10个， 会这根据条件查询", response_model=ResponseBase[list[SessionInfo]])
async def list_sessions(
    params: SessionListParams,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ResponseBase[list[SessionInfo]]:
    
    sessions =await chat_service.query_sessions(db, params= params)
    return ResponseBase(data=[ SessionInfo.model_validate(session) for session in sessions] if sessions else [])


# # ──────────────────────── 会话详情 ────────────────────────

@router.get("/sessions/{session_id}", summary="获取会话详情")
async def get_session(
    session_id: str,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ResponseBase[SessionDetail]:
   
    session =await chat_service.get_chat_session(session_id, db)

    return ResponseBase(data=SessionDetail.model_validate(session) if session else None)


# ──────────────────────── 重命名会话 ────────────────────────

@router.put("/sessions/rename", summary="重命名会话")
async def rename_session(
    body: RenameRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ResponseBase[SessionInfo]:

    session =await chat_service.get_chat_session(body.session_id, db)
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session.name = body.name
    session = await chat_service.update_session(SessionInfo.model_validate(session), db=db)

    return ResponseBase(data=SessionInfo.model_validate(session) if session else None)
