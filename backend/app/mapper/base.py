# 增删改查基类

from __future__ import annotations
from datetime import datetime
from typing import Generic, Type, TypeVar, Any, overload
import pydantic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import CursorResult, func, select, update, delete
from sqlalchemy.sql import ColumnElement
from app.models.base import BaseModel, LogicDeleteMixin
from app.schemas.base import PaginatedResponse

ModelType = TypeVar("ModelType", bound=BaseModel)
T = TypeVar("T", bound=pydantic.BaseModel)


class CRUDBase(Generic[ModelType]):
    """CRUD 基类"""
    
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model
        
    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """根据 ID 获取记录"""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """获取多条记录"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    
    @overload
    async def get_page(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        filters: dict[str, Any] | None = None,
        order_by: tuple[str, str] | None = None,
        ignore_deleted: bool = True,
        schema: None = None,
    ) -> PaginatedResponse[ModelType]: ...
    
    @overload
    async def get_page(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        filters: dict[str, Any] | None = None,
        order_by: tuple[str, str] | None = None,
        ignore_deleted: bool = True,
        schema: Type[T],
    ) -> PaginatedResponse[T]: ...
    
    async def get_page(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        filters: dict[str, Any] | None = None,
        order_by: tuple[str, str] | None = None,
        ignore_deleted: bool = True,
        schema: Type[T] | None = None,
    ) -> PaginatedResponse[ModelType] | PaginatedResponse[T]:
        """
        分页查询
        
        Args:
            page_num: 页码，从 1 开始
            page_size: 每页数量
            filters: 过滤条件，格式 {"field": value} 或 {"field": ("op", value)}
                     支持操作符: ==, !=, >, <, >=, <=, like, in
            order_by: 排序，格式 ("field", "asc" | "desc")
            ignore_deleted: 是否自动过滤逻辑删除记录
            schema: 可选的 Pydantic schema 类，用于将 ORM 对象转换为指定格式
        
        Returns:
            PaginatedResponse 包含 items, total, page, page_size, total_pages
            如果传入 schema 参数，items 为 schema 类型列表；否则为 ModelType 列表
        """
        query = select(self.model)
        
        # 自动过滤逻辑删除记录
        if ignore_deleted and issubclass(self.model, LogicDeleteMixin):
            query = query.where(self.model.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            for field, condition in filters.items():
                column = getattr(self.model, field, None)
                if column is None or condition is None:
                    continue
                query = query.where(self._build_filter_condition(column, condition))
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        # 应用排序
        if order_by:
            field, direction = order_by
            column = getattr(self.model, field, None)
            if column is not None:
                query = query.order_by(column.desc() if direction == "desc" else column.asc())
        
        # 分页查询
        offset = (page_num - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())
        
        # 转换为指定 schema 类型
        if schema is not None:
            items = [schema.model_validate(item) for item in items]
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return PaginatedResponse(
            items=items, # type: ignore
            total=total,
            page=page_num,
            page_size=page_size,
            total_pages=total_pages,
        )
    
    def _build_filter_condition(
        self, column: Any, condition: Any
    ) -> ColumnElement[bool]:
        """构建过滤条件"""
        if isinstance(condition, tuple):
            op, value = condition
            if op == "==":
                return column == value
            elif op == "!=":
                return column != value
            elif op == ">":
                return column > value
            elif op == "<":
                return column < value
            elif op == ">=":
                return column >= value
            elif op == "<=":
                return column <= value
            elif op == "like":
                return column.like(value)
            elif op == "in":
                return column.in_(value)
            else:
                return column == value
        else:
            return column == condition
    
    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ModelType:
        """创建记录"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        """更新记录"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: AsyncSession, *, id: int) -> ModelType | None:
        """删除记录"""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
    
    async def remove_logic(self, db: AsyncSession, *, ids: list[int]) -> int:
        """删除记录"""
        if not issubclass(self.model, LogicDeleteMixin):
            raise ValueError(f"模型{self.model.__name__}未继承LogicDeleteMixin类,默认不支持逻辑删除")
        result = await db.execute(
            update(self.model)
            .where(self.model.id.in_(ids), self.model.is_deleted == False)
            .values(
                is_deleted=True,
                deleted_at = datetime.now()
            )
        )
        await db.flush()
        cursor_result: CursorResult = result # type: ignore
        return cursor_result.rowcount