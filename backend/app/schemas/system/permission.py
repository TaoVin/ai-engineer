"""权限相关 Schema（DTO）"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.enums.system import PermissionType
from app.schemas.system.role import RoleResponse


class PermissionResponse(BaseModel):
    """权限响应 Schema（用于 API 返回，过滤敏感字段如 password）"""

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
        
class PermissionCreate(BaseModel):
    """创建权限请求 Schema"""
    permission_name: str = Field(..., description="权限名")
    parent_id: int = Field(default=0, description="父级权限id")
    permission_key: str | None = Field(None, description="权限标识")
    permission_type: PermissionType = Field(..., description="权限类型")
    sort: int = Field(..., description="权限排序")
    path: str = Field(..., description="路由路径")

class PermissionDto(BaseModel):
    """创建权限请求 Schema"""
    id: int = Field(..., description="主键ID")
    permission_name: str = Field(..., description="权限名")
    parent_id: int = Field(default=0, description="父级权限id")
    permission_key: str | None = Field(None, description="权限标识")
    permission_type: PermissionType = Field(..., description="权限类型")
    sort: int = Field(..., description="权限排序")
    path: str = Field(..., description="路由路径")
    

class PermissionParam(BaseModel):
    """权限查询 Schema"""
    id: Optional[int] = Field(default=None, gt=0, description="主键ID")
    permission_name: Optional[str] = Field(default=None, description="权限名")
    parent_id: Optional[int] = Field(default=None, description="父级权限id")
    permission_key: Optional[str] | None = Field(None, description="权限标识")
    permission_type: Optional[PermissionType] = Field(default=None, description="权限类型")
    path: Optional[str] = Field(default=None, description="路由路径")
    
    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        """处理 id 为 0 的情况"""
        if v in (0, "0"):
            return None  # 将 0 转换为 None
        return v