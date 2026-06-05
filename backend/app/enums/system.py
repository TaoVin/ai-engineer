"""系统管理模块枚举"""

from enum import Enum


class PermissionType(str, Enum):
    """权限类型枚举"""
    # 菜单权限
    MENU = "M"
    # 按钮权限
    BUTTON = "B"
    # 接口权限
    API = "A"
    # 链接
    LINK = "L"
