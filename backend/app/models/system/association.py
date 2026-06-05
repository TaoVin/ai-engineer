

from sqlalchemy import ForeignKey, Integer, Nullable, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship


from app.models.base import BaseModel
from app.models.system.permission import Permission
from app.models.system.role import Role
from app.models.system.user import User


class UserRole(BaseModel):
    """用户角色关联模型"""
    __tablename__="sys_user_role"
    
    user_id: Mapped[int] = mapped_column(
        Integer,  ForeignKey("sys_user.id"), nullable=False, comment="用户id"
    )
    role_id: Mapped[int] = mapped_column(
        Integer,  ForeignKey("sys_role.id"), nullable=False, comment="角色id"
    )
    
    user: Mapped[User] =relationship("User")
    role: Mapped[Role] =relationship("Role")
    
    # 联合唯一
    
    __table_args__=(
        UniqueConstraint('user_id', 'role_id',  name='uq_user_role'),
    )
    
class RolePermission(BaseModel):
    """角色权限关联模型"""
    __tablename__="sys_role_permission"
        
    role_id: Mapped[int] = mapped_column(
        Integer,  ForeignKey("sys_role.id"), nullable=False, comment="用户id"
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,  ForeignKey("sys_permission.id"), nullable=False, comment="角色id"
    )
    
    permission: Mapped[Permission] =relationship("Permission")
    role: Mapped[Role] =relationship("Role")
    
    # 联合唯一
    
    __table_args__=(
        UniqueConstraint('role_id', 'permission_id',  name='uq_role_permission'),
    )