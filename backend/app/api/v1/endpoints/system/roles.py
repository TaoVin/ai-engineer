"""角色控制器"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.service.system import get_user_service
from app.service.system.user_service import UserService
from app.schemas.base import ResponseBase
from app.schemas.system.user import UserResponse

router = APIRouter()


@router.get("/query/byName", response_model=ResponseBase[UserResponse])
async def get_user(
    userName: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_by_username(db, username=userName)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)
