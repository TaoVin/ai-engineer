from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.system import PermissionType
from app.models.base import BaseModel, LogicDeleteMixin


if TYPE_CHECKING:
    # 仅在类型检查时导入，避免循环依赖
    from .role import Role

class Permission(BaseModel, LogicDeleteMixin):
    """权限模型"""

    __tablename__ = "sys_permission"

    # 权限名称
    permission_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="权限名"
    )

    parent_id: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="父级权限id"
    )

    permission_key: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="权限标识"
    )

    permission_type: Mapped[PermissionType] = mapped_column(
        nullable=False, comment="权限类型"
    )

    sort: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="权限排序"
    )

    path: Mapped[str] = mapped_column(String(200), nullable=True, comment="路由路径")

    # 使用字符串引用避免循环导入
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="sys_role_permission",
        back_populates="permissions",
        lazy="select",
    )

    