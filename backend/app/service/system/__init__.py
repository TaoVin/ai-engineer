"""系统管理服务"""

from typing import AsyncGenerator

from app.service.system.permission_service import PermissionService
from app.service.system.role_service import RoleService
from app.service.system.user_service import UserService


async def get_user_service() -> AsyncGenerator[UserService, None]:
    """获取用户服务实例"""
    yield UserService()


async def get_role_service() -> AsyncGenerator[RoleService, None]:
    """获取角色服务实例"""
    yield RoleService()


async def get_permission_service() -> AsyncGenerator[PermissionService, None]:
    """获取权限服务实例"""
    yield PermissionService()
