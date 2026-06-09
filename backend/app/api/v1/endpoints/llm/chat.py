
import json
from datetime import datetime
from typing import Annotated

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

router = APIRouter()

# Redis key 模式
_SESSION = "chat:session:{}"
_MESSAGES = "chat:session:{}:messages"
_INDEX = "chat:sessions"


# ──────────────────────── 流式聊天 ────────────────────────

@router.post("/stream", summary="流式聊天")
async def chat_stream(
    chat_req: ChatRequest,
    client: Annotated[AsyncOpenAI, Depends(get_client)],
):
    session_id = chat_req.session_id
    user_message = chat_req.message
    meta_key = _SESSION.format(session_id)
    msgs_key = _MESSAGES.format(session_id)

    now = datetime.now()
    session_exists = await redis_manager.hexists(meta_key, "name")

    if not session_exists:
        await redis_manager.hset_dict(meta_key, {
            "name": user_message[:20],
            "create_time": now.isoformat(),
            "last_time": now.isoformat(),
            "create_id": 0,
        })
        await redis_manager.zadd(_INDEX, {session_id: now.timestamp()})

    # 追加用户消息
    await redis_manager.rpush(msgs_key, {
        "role": "user",
        "content": user_message,
    })

    # 更新最后活跃时间 & 索引
    now_iso = now.isoformat()
    now_ts = now.timestamp()
    await redis_manager.hset(meta_key, "last_time", now_iso)
    await redis_manager.zadd(_INDEX, {session_id: now_ts})

    # 加载全部消息供 AI 调用
    raw_messages = await redis_manager.lrange(msgs_key, 0, -1)
    openai_messages = [{"role": m["role"], "content": m["content"]} for m in raw_messages]

    async def event_generator():
        full_response = ""
        async for data in stream_ai_response(openai_messages, client):
            yield f"data: {data}\n\n"

            obj = json.loads(data)
            if obj.get("type") == "token":
                full_response += obj["content"]
            elif obj.get("type") == "done":
                finished_at = datetime.now()
                await redis_manager.rpush(msgs_key, {
                    "role": "assistant",
                    "content": full_response,
                })
                await redis_manager.hset(meta_key, "last_time", finished_at.isoformat())
                await redis_manager.zadd(_INDEX, {session_id: finished_at.timestamp()})
            elif obj.get("type") == "error":
                print(f"Stream error: {obj['content']}")

    return EventSourceResponse(event_generator())


# ──────────────────────── 会话列表 ────────────────────────

@router.get("/sessions", summary="获取会话列表")
async def list_sessions(
    params: Annotated[SessionListParams, Depends()],
) -> ResponseBase[PaginatedResponse[SessionInfo]]:
    total = await redis_manager.zcard(_INDEX)
    if total == 0:
        return ResponseBase(data=PaginatedResponse[SessionInfo](
            items=[], total=0, page=params.page, page_size=params.page_size, total_pages=0,
        ))

    start = (params.page - 1) * params.page_size
    end = start + params.page_size - 1
    session_ids = await redis_manager.zrevrange(_INDEX, start, end)

    items: list[SessionInfo] = []
    for sid in session_ids:
        meta = await redis_manager.hgetall(_SESSION.format(sid))
        if not meta:
            continue
        msg_count = await redis_manager.llen(_MESSAGES.format(sid))
        items.append(SessionInfo(
            session_id=sid,
            name=meta.get("name", ""),
            create_time=datetime.fromisoformat(meta["create_time"]),
            last_time=datetime.fromisoformat(meta["last_time"]),
            message_count=msg_count,
        ))

    total_pages = (total + params.page_size - 1) // params.page_size
    return ResponseBase(data=PaginatedResponse[SessionInfo](
        items=items, total=total, page=params.page, page_size=params.page_size,
        total_pages=total_pages,
    ))


# ──────────────────────── 会话详情 ────────────────────────

@router.get("/sessions/{session_id}", summary="获取会话详情")
async def get_session(
    session_id: str,
) -> ResponseBase[SessionDetail]:
    meta_key = _SESSION.format(session_id)
    msgs_key = _MESSAGES.format(session_id)

    meta = await redis_manager.hgetall(meta_key)
    if not meta:
        raise HTTPException(status_code=404, detail="会话不存在")

    raw_messages = await redis_manager.lrange(msgs_key, 0, -1)
    messages = [MessageItem(role=m["role"], content=m["content"]) for m in raw_messages]

    return ResponseBase(data=SessionDetail(
        session_id=session_id,
        name=meta.get("name", ""),
        create_time=datetime.fromisoformat(meta["create_time"]),
        last_time=datetime.fromisoformat(meta["last_time"]),
        messages=messages,
    ))


# ──────────────────────── 重命名会话 ────────────────────────

@router.put("/sessions/{session_id}/name", summary="重命名会话")
async def rename_session(
    session_id: str,
    body: RenameRequest,
) -> ResponseBase[SessionInfo]:
    meta_key = _SESSION.format(session_id)

    exists = await redis_manager.exists(meta_key)
    if not exists:
        raise HTTPException(status_code=404, detail="会话不存在")

    await redis_manager.hset(meta_key, "name", body.name)
    meta = await redis_manager.hgetall(meta_key)
    msg_count = await redis_manager.llen(_MESSAGES.format(session_id))

    return ResponseBase(data=SessionInfo(
        session_id=session_id,
        name=body.name,
        create_time=datetime.fromisoformat(meta["create_time"]),
        last_time=datetime.fromisoformat(meta["last_time"]),
        message_count=msg_count,
    ))
