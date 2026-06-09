
import json
from datetime import datetime
from typing import Annotated

from app.core.deps import get_db
from app.enums.llm import MessageRole
from app.models.llm.chat import ChatSession
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

    if not session:
        session = ChatSession(name = user_message[0: 10], session_id = session_id, last_time=datetime.now())
    
    session.last_time = datetime.now()
    await chat_service.update_session(session, db)
    
    messags = session.messages
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
                await chat_service.save_message(call_back_message)
            elif obj.get("type") == "error":
                print(f"Stream error: {obj['content']}")

    return EventSourceResponse(event_generator())


# # ──────────────────────── 会话列表 ────────────────────────

# @router.get("/sessions", summary="获取会话列表")
# async def list_sessions(
#     params: Annotated[SessionListParams, Depends()],
# ) -> ResponseBase[PaginatedResponse[SessionInfo]]:
#     total = await redis_manager.zcard(_INDEX)
#     if total == 0:
#         return ResponseBase(data=PaginatedResponse[SessionInfo](
#             items=[], total=0, page=params.page, page_size=params.page_size, total_pages=0,
#         ))

#     start = (params.page - 1) * params.page_size
#     end = start + params.page_size - 1
#     session_ids = await redis_manager.zrevrange(_INDEX, start, end)

#     items: list[SessionInfo] = []
#     for sid in session_ids:
#         meta = await redis_manager.hgetall(_SESSION.format(sid))
#         if not meta:
#             continue
#         msg_count = await redis_manager.llen(_MESSAGES.format(sid))
#         items.append(SessionInfo(
#             session_id=sid,
#             name=meta.get("name", ""),
#             create_time=datetime.fromisoformat(meta["create_time"]),
#             last_time=datetime.fromisoformat(meta["last_time"]),
#             message_count=msg_count,
#         ))

#     total_pages = (total + params.page_size - 1) // params.page_size
#     return ResponseBase(data=PaginatedResponse[SessionInfo](
#         items=items, total=total, page=params.page, page_size=params.page_size,
#         total_pages=total_pages,
#     ))


# # ──────────────────────── 会话详情 ────────────────────────

# @router.get("/sessions/{session_id}", summary="获取会话详情")
# async def get_session(
#     session_id: str,
# ) -> ResponseBase[SessionDetail]:
#     meta_key = _SESSION.format(session_id)
#     msgs_key = _MESSAGES.format(session_id)

#     meta = await redis_manager.hgetall(meta_key)
#     if not meta:
#         raise HTTPException(status_code=404, detail="会话不存在")

#     raw_messages = await redis_manager.lrange(msgs_key, 0, -1)
#     messages = [MessageItem(role=m["role"], content=m["content"]) for m in raw_messages]

#     return ResponseBase(data=SessionDetail(
#         session_id=session_id,
#         name=meta.get("name", ""),
#         create_time=datetime.fromisoformat(meta["create_time"]),
#         last_time=datetime.fromisoformat(meta["last_time"]),
#         messages=messages,
#     ))


# # ──────────────────────── 重命名会话 ────────────────────────

# @router.put("/sessions/{session_id}/name", summary="重命名会话")
# async def rename_session(
#     session_id: str,
#     body: RenameRequest,
# ) -> ResponseBase[SessionInfo]:
#     meta_key = _SESSION.format(session_id)

#     exists = await redis_manager.exists(meta_key)
#     if not exists:
#         raise HTTPException(status_code=404, detail="会话不存在")

#     await redis_manager.hset(meta_key, "name", body.name)
#     meta = await redis_manager.hgetall(meta_key)
#     msg_count = await redis_manager.llen(_MESSAGES.format(session_id))

#     return ResponseBase(data=SessionInfo(
#         session_id=session_id,
#         name=body.name,
#         create_time=datetime.fromisoformat(meta["create_time"]),
#         last_time=datetime.fromisoformat(meta["last_time"]),
#         message_count=msg_count,
#     ))
