from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, LogicDeleteMixin

if TYPE_CHECKING:
    # 仅在类型检查时导入，避免循环依赖
    from .user import User
    from .permission import Permission
    
    
class Role(BaseModel,LogicDeleteMixin):
    """角色模型"""

    __tablename__ = "sys_role"

    # 角色名
    role_name: Mapped[str] = mapped_column(String(50), unique=True, comment="角色名")

    # 角色键值
    role_key: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="角色键值"
    )

    description: Mapped[str] = mapped_column(
        String(200), nullable=True, comment="角色描述"
    )

    sort: Mapped[int] = mapped_column(Integer, default=0, comment="角色排序")

    # 使用字符串引用避免循环导入
    # 注意: 必须显式指定 primaryjoin/secondaryjoin，因为 BaseModel 的
    # created_id/updated_id 导致 sys_user_role 表有多个 FK 指向 sys_user
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="sys_user_role",
        back_populates="roles",
        lazy="selectin",
        primaryjoin="Role.id == foreign(UserRole.role_id)",
        secondaryjoin="foreign(UserRole.user_id) == User.id"
    )

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="sys_role_permission",
        back_populates="roles",
        lazy="selectin",
    )
