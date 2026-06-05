"""角色相关 Schema（DTO）"""

from pydantic import BaseModel, Field


class RoleResponse(BaseModel):
    """角色响应 Schema"""

    id: int = Field(..., description="主键ID")
    role_name: str = Field(..., description="角色名称")
    role_key: str = Field(..., description="角色键值")
    description: str | None = Field(None, description="角色描述")
    sort: int = Field(0, description="排序")

    class Config:
        from_attributes = True
