from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from app.core.database import async_session_factory

from app.core.security import verify_token
from app.models.system.role import Role
from app.models.system.user import User
from app.schemas.system.user import LoginUserResponse
from app.service.system import get_user_service
from app.service.system.user_service import UserService


'''
AsyncGenerator：异步生成器类型
async with：异步上下文管理器
yield：依赖注入中的会话提供
commit()：提交事务
rollback()：回滚事务
close()：关闭会话
'''
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """ 获取数据库会话 """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    

# ============================================================
# 第一层：解析 Token → 获取用户
# ============================================================

async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> LoginUserResponse:
    """
    从请求头解析 Token，获取当前用户

    流程：
    1. 从 Authorization: Bearer <token> 提取 token
    2. 解码 JWT，获取 user_id
    3. 查询数据库获取用户（同时加载角色和权限）
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception

    token = authorization.removeprefix("Bearer ")

    # 解码 Token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    # 验证令牌类型（必须是 access token）
    if payload.get("type") != "access":
        raise credentials_exception

    # 获取用户 ID
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 查询用户（预加载角色和权限）
    user = await user_service.query_by_id(db, id = int(str(user_id)))

    # result = await db.execute(
    #     select(User)
    #     .options(selectinload(User.roles).selectinload(Role.permissions))
    #     .where(User.id == int(str(user_id)))
    # )
    # user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    
    response = LoginUserResponse.model_validate(user)
    response.role_keys = {role.role_key for role in user.roles}
    response.permission_keys = {
        p.permission_key 
        for role in user.roles
        for p in role.permissions 
    }
    return response
