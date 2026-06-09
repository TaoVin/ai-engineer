# 用户类模型

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from app.enums.llm import MessageRole
from app.models.base import BaseModel, LogicDeleteMixin


class ChatMessage(BaseModel, LogicDeleteMixin):
    """消息模型"""

    __tablename__ = "chat_message"


    session_id: Mapped[str] = mapped_column(
        String(50),
        index=True,
        comment="会话id"
    )
    content: Mapped[str] = mapped_column(
        LONGTEXT,
        nullable=False,
        comment="消息"
    )

    role: Mapped[MessageRole] = mapped_column(
        nullable=False,
        comment="消息角色"
    )


    name: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="消息名称"
    )

    tool_call_id:  Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="工具调用id"
    )

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
    
class ChatSession(BaseModel, LogicDeleteMixin):
    """会话模型"""

    __tablename__ = "chat_session"


    session_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="会话对外唯一表识"
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="会话名称"
    )
    
    last_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="最后一次提问时间"
    )


    messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage",
        back_populates="session"
    )





