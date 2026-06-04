# 统一返回格式

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field
from starlette import status

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    code: int = Field(default=status.HTTP_200_OK, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: T | None = Field(default=None, description="数据")
    extra: Any = Field(default=None, description="额外信息")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""

    items: list[T] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=10, description="每页数量")
    total_pages: int = Field(default=1, description="总页数")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    code: int = Field(
        default=status.HTTP_500_INTERNAL_SERVER_ERROR, description="错误码"
    )
    message: str = Field(default="系统异常", description="错误消息")
    detail: Any | None = Field(None, description="详细信息")
