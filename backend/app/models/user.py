# 用户类模型

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):
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
        comment="名字"
    )
    
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="邮箱"
    )
    
    password: Mapped[str] = mapped_column(
        String(256),
        comment="密码"
    )
     
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.user_name})>"
    
