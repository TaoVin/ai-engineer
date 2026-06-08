"""认证模块"""

import random
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException,status

from app.config.settings import setting
from app.core.deps import get_current_user, get_db
from app.core.redis import redis_manager
from app.core.security import create_access_token, create_refresh_token, verify_password, verify_token
from app.models.system.user import User
from app.schemas.base import ResponseBase
from app.schemas.system.auth import LoginDto, LoginResponse, RefreshTokenRequest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.system.user import LoginUserResponse, UserResponse
from app.service.system import get_user_service
from app.service.system.user_service import UserService

router = APIRouter()


@router.get("/code", summary="获取随机验证码", description="实际使用需转成图片返回")
async def get_login_code():
    code = random.randint(1000, 9999)
    # 存入 Redis，5 分钟过期（后续登录时校验）
    await redis_manager.cache_set(f"captcha:{code}", code, expire=300)
    return ResponseBase(data={"code": code})






@router.post("/login", summary="登录", response_model=ResponseBase[LoginResponse])
async def login(dto: LoginDto, db: Annotated[AsyncSession, Depends(get_db)], user_service: Annotated[UserService, Depends(get_user_service)]) -> ResponseBase[LoginResponse]:
    result = await redis_manager.cache_get(f"captcha:{dto.code}")
    if not result:
        raise ValueError("验证号码已经过期")

    user = await user_service.get_by_username(db, username=dto.user_name)
    if not user or not verify_password(dto.user_pwd, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
        
    return ResponseBase(data=LoginResponse(access_token=access_token, refresh_token=refresh_token))

@router.post("/refresh", response_model=ResponseBase[LoginResponse], summary="刷新token")
async def refresh_token(
    token_in: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    payload = verify_token(token_in.refresh_token)
    if not payload or payload.get("type") != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
        )
    user = await user_service.query_by_id(db, id=int(str(user_id)))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="认证失败"
        )
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return ResponseBase(data=LoginResponse(access_token=access_token, refresh_token=refresh_token))


@router.get("/me", response_model=ResponseBase[LoginUserResponse])
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取当前登录用户信息"""
    return ResponseBase(data=LoginUserResponse.model_validate(current_user))