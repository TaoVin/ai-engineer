from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Integer, false, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# DeclarativeBase SQLAlchemy 2.0 的声明式基类
class Base(DeclarativeBase):
    """SQLAlchemy 基类"""

    # 允许任意类型
    type_annotation_map = {
        dict[str, Any]: dict,
    }


class BaseModel(Base):
    """
    带主键的基础模型

    所有业务模型都应继承此类，自动拥有：
    - id: 主键
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __abstract__ = True  # 声明为抽象类，不会创建表

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键ID"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
        comment="更新时间",
    )


# class IdMixin:
#     """主键混入类"""

#     id: Mapped[int] = mapped_column(
#         Integer,
#         primary_key=True,
#         autoincrement=True,
#         comment="主键ID"
#     )


class LogicDeleteMixin:
    """逻辑删除混入类，代码复用模式"""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=false, comment="逻辑删除标记"
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="删除时间"
    )
