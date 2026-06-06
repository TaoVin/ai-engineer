"""认证模块"""

import random
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException,status

from app.config.settings import setting
from app.core.deps import get_db
from app.core.redis import redis_manager
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.schemas.base import ResponseBase
from app.schemas.system.auth import LoginDto, LoginResponse
from sqlalchemy.ext.asyncio import AsyncSession

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
    
    # accesstoken 有效期设置分钟
    await redis_manager.cache_set(f"access:{access_token}", user, expire=setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    # refresh_token 有效期设置天
    await redis_manager.cache_set(f"access:{refresh_token}", access_token, expire=setting.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    
    return ResponseBase(data=LoginResponse(access_token=access_token, refresh_token=refresh_token))
