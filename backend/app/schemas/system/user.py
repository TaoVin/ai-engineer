"""用户相关 Schema（DTO）"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.system.role import RoleResponse


class UserResponse(BaseModel):
    """用户响应 Schema（用于 API 返回，过滤敏感字段如 password）"""

    id: int = Field(..., description="主键ID")
    user_name: str = Field(..., description="登陆账号")
    nick_name: str = Field(..., description="名字")
    email: str | None = Field(None, description="邮箱")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    roles: list[RoleResponse] = Field(default_factory=list, description="角色列表")

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """创建用户请求 Schema"""

    user_name: str = Field(..., min_length=2, max_length=50, description="登陆账号")
    nick_name: str = Field(..., min_length=1, max_length=50, description="名字")
    email: EmailStr | None = Field(None, description="邮箱")
    password: str = Field(..., min_length=6, max_length=256, description="密码")


class UserDto(BaseModel):
    """更新用户请求 Schema"""

    id: int = Field(..., description="主键ID")
    nick_name: str | None = Field(None, description="名字")
    email: str | None = Field(None, description="邮箱")
    

class UserPasswordUpdate(BaseModel):
    """更新用户密码请求 Schema"""
    id: int = Field(..., description="主键ID")
    password: str = Field(..., min_length=6, max_length=256, description="密码")


class UserParam(BaseModel):
    """用户查询 Schema"""

    id: Optional[int] = Field(default=None, gt=0, description="主键ID")
    user_name: Optional[str] = Field(default=None, description="登陆账号")
    nick_name: Optional[str] = Field(default=None, description="名字")
    email: Optional[str] = Field(default=None, description="邮箱")

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        """处理 id 为 0 的情况"""
        if v in (0, "0"):
            return None
        return v


class UserBindRoleDto(BaseModel):
    """用户绑定角色请求 Schema"""

    id: int = Field(..., description="用户主键id")
    role_ids: list[int] = Field(default=[], description="角色id集合")
