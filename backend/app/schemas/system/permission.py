"""权限相关 Schema（DTO）"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.enums.system import PermissionType
from app.schemas.system.role import RoleResponse


class PermissionResponse(BaseModel):
    """用户响应 Schema（用于 API 返回，过滤敏感字段如 password）"""

    id: int = Field(..., description="主键ID")
    permission_name: str = Field(..., description="权限名")
    parent_id: int = Field(..., description="父级权限id")
    permission_key: str | None = Field(None, description="权限标识")
    permission_type: PermissionType = Field(..., description="权限类型")
    sort: int = Field(..., description="权限排序")
    path: str = Field(..., description="路由路径")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class PermissionDto(BaseModel):
    """创建用户请求 Schema"""
    id: int = Field(..., description="主键ID")
    permission_name: str = Field(..., description="权限名")
    parent_id: int = Field(default=0, description="父级权限id")
    permission_key: str | None = Field(None, description="权限标识")
    permission_type: PermissionType = Field(..., description="权限类型")
    sort: int = Field(..., description="权限排序")
    path: str = Field(..., description="路由路径")
    
    
