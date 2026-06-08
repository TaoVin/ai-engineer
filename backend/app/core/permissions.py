from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.core.deps import get_current_user
from app.schemas.system.user import LoginUserResponse


class require_permission:
    """
    权限检查依赖类（可调用类）

    用法：
        @router.get("/users", dependencies=[Depends(require_permission("user:read"))])
        async def list_users():
            ...

    或者：
        async def list_users(
            user: Annotated[User, Depends(require_permission("user:read"))]
        ):
            ...
    """

    def __init__(self, permission_code: str):
        self.permission_code = permission_code

    async def __call__(
        self,
        current_user: Annotated[LoginUserResponse, Depends(get_current_user)],
    ) -> LoginUserResponse:
        
        # 超级管理员拥有所有权限
        if "*" in current_user.permission_keys:
            return current_user

        if self.permission_code not in current_user.permission_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限：{self.permission_code}",
            )

        return current_user


class require_any_permission:
    """
    检查用户是否拥有任意一个权限

    用法：
        @router.get("/users", dependencies=[
            Depends(require_any_permission("user:read", "user:manage"))
        ])
    """

    def __init__(self, *permission_codes: str):
        self.permission_codes = set(permission_codes)

    async def __call__(
        self,
        current_user: Annotated[LoginUserResponse, Depends(get_current_user)],
    ) -> LoginUserResponse:

        if "*" in current_user.permission_keys:
            return current_user

        if not self.permission_codes & current_user.permission_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要以下权限之一：{', '.join(self.permission_codes)}",
            )
        return current_user
    
    
class require_role:
    """
    角色检查依赖类（可调用类）

    用法：
        @router.get("/users", dependencies=[Depends(require_role("admin"))])
        async def list_users():
            ...

    或者：
        async def list_users(
            user: Annotated[User, Depends(require_role("admin"))]
        ):
            ...
    """

    def __init__(self, role_code: str):
        self.role_code = role_code

    async def __call__(
        self,
        current_user: Annotated[LoginUserResponse, Depends(get_current_user)],
    ) -> LoginUserResponse:

        if self.role_code not in current_user.role_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色不足，需要角色：{self.role_code}",
            )

        return current_user


class require_any_role:
    """
    检查用户是否拥有任意一个角色

    用法：
        @router.get("/users", dependencies=[
            Depends(require_any_role("admin", "operator"))
        ])
    """

    def __init__(self, *role_codes: str):
        self.role_codes = set(role_codes)

    async def __call__(
        self,
        current_user: Annotated[LoginUserResponse, Depends(get_current_user)],
    ) -> LoginUserResponse:

        if not self.role_codes & current_user.role_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色不足，需要以下角色之一：{', '.join(self.role_codes)}",
            )
        return current_user