"""认证模块"""

import random

from fastapi import APIRouter

from app.core.redis import redis_manager
from app.schemas.base import ResponseBase

router = APIRouter()


@router.get("/code", summary="获取随机验证码", description="实际使用需转成图片返回")
async def get_login_code():
    code = random.randint(1000, 9999)
    # 存入 Redis，5 分钟过期（后续登录时校验）
    await redis_manager.cache_set(f"captcha:{code}", code, expire=300)
    return ResponseBase(data={"code": code})





