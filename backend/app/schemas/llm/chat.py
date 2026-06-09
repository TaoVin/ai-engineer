from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.enums.llm import MessageRole


class ChatRequest(BaseModel):
    """问答参数"""

    session_id: str = Field(..., description="会话id")
    message: str = Field(..., description="消息")


class MessageItem(BaseModel):
    """消息记录"""
    role: MessageRole = Field(..., description="角色")
    content: str = Field(..., description="内容")
    session_id: str = Field(..., description="会话id")
    name: Optional[str] = Field(..., description="消息名称")
    tool_call_id: Optional[str] = Field(..., description="工具调用id")
    created_at: datetime = Field(..., description="创建时间")


class RenameRequest(BaseModel):
    """重命名请求"""
    name: str = Field(..., description="会话名称", min_length=1, max_length=100)


class SessionListParams(BaseModel):
    """会话列表查询参数"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class SessionInfo(BaseModel):
    """会话列表项"""
    session_id: str = Field(..., description="会话id")
    name: str = Field(..., description="会话名称")
    create_time: datetime = Field(..., description="创建时间")
    last_time: datetime = Field(..., description="最后活跃时间")
    message_count: int = Field(..., description="消息数量")


class SessionDetail(BaseModel):
    """会话详情"""

    session_id: str = Field(..., description="会话id")
    name: str = Field(..., description="会话名称")
    create_time: datetime = Field(..., description="创建时间")
    last_time: datetime = Field(..., description="最后活跃时间")
    messages: list[MessageItem] = Field(..., description="消息列表")
