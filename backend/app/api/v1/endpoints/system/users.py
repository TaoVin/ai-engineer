"""用户控制器"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.deps import get_db
from app.crud.crud_user import user_crud
from app.schemas.base import ResponseBase
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/query/byName", response_model=ResponseBase[UserResponse])
async def get_user(
    userName: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await user_crud.get_by_username(db, username=userName)
    return ResponseBase(data=UserResponse.model_validate(user) if user else None)
    
    