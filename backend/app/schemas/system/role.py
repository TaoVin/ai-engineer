"""角色相关 Schema（DTO）"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RoleResponse(BaseModel):
    """角色响应 Schema"""

    id: int = Field(..., description="主键ID")
    role_name: str = Field(..., description="角色名称")
    role_key: str = Field(..., description="角色键值")
    description: str | None = Field(None, description="角色描述")
    sort: int = Field(0, description="排序")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """创建角色请求 Schema"""

    role_name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    role_key: str = Field(..., min_length=1, max_length=50, description="角色键值")
    description: str | None = Field(None, max_length=200, description="角色描述")
    sort: int = Field(default=0, description="排序")


class RoleDto(BaseModel):
    """更新角色请求 Schema"""

    id: int = Field(..., description="主键ID")
    role_name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    role_key: str = Field(..., min_length=1, max_length=50, description="角色键值")
    description: str | None = Field(None, max_length=200, description="角色描述")
    sort: int = Field(default=0, description="排序")


class RoleParam(BaseModel):
    """角色查询 Schema"""

    id: Optional[int] = Field(default=None, gt=0, description="主键ID")
    role_name: Optional[str] = Field(default=None, description="角色名称")
    role_key: Optional[str] = Field(default=None, description="角色键值")
    description: Optional[str] = Field(default=None, description="角色描述")
    sort: Optional[int] = Field(default=None, description="排序")

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        """处理 id 为 0 的情况"""
        if v in (0, "0"):
            return None
        return v
    
class RoleBindPermissionDto(BaseModel):
    """角色绑定权限请求 Schema"""
    id: int = Field(..., description="角色主键id")
    permission_ids: list[int] = Field(default=[], description="权限id集合") 