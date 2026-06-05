"""用户相关 Schema（DTO）"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

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
    role_id_list: list[int] = Field(..., description="用户角色关联")



class UserUpdate(BaseModel):
    """更新用户请求 Schema"""
    id: int = Field(..., description="主键ID")
    nick_name: str | None = Field(None, description="名字")
    email: str | None = Field(None, description="邮箱")
    role_id_list: list[int] = Field(..., description="用户角色关联")
    
class UserPassworddUpdate(BaseModel):
    """更新用户密码请求 Schema"""
    id: int = Field(..., description="主键ID")
    password: str = Field(..., min_length=6, max_length=256, description="密码")
