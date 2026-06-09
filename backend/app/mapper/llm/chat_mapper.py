

from app.mapper.base import CRUDBase
from app.models.llm.chat import ChatSession, ChatMessage


class ChatSessionMapper(CRUDBase[ChatSession]):
    """会话CRUD 操作"""

chat_session_crud = ChatSessionMapper(ChatSession)



class ChatMessageMapper(CRUDBase[ChatMessage]):
    """消息CRUD 操作"""

chat_message_crud = ChatMessageMapper(ChatMessage)