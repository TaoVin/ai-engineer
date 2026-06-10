# 用户类模型

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, LogicDeleteMixin

if TYPE_CHECKING:
    # 仅在类型检查时导入，避免循环依赖
    from .role import Role
    
class User(BaseModel, LogicDeleteMixin):
    """用户模型"""

    __tablename__ = "sys_user"

    # 用户名
    user_name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="登陆账号"
    )
    nick_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="名字"
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="邮箱"
    )

    password: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="密码"
    )

    # 使用字符串引用避免循环导入
    # 注意: 必须显式指定 primaryjoin/secondaryjoin，因为 BaseModel 的
    # created_id/updated_id 导致 sys_user_role 表有多个 FK 指向 sys_user
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="sys_user_role",
        back_populates="users",
        lazy="selectin",
        primaryjoin="User.id == foreign(UserRole.user_id)",
        secondaryjoin="foreign(UserRole.role_id) == Role.id"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.user_name})>"
