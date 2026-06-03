# 步骤5：RESTful API 开发

## 5.1 知识点概述

RESTful API 是现代 Web 应用的核心，本节将学习如何设计和实现规范的 REST API。

### 核心概念

- **REST（Representational State Transfer）**：表述性状态转移架构风格
- **资源（Resource）**：API 操作的对象
- **HTTP 方法**：GET、POST、PUT、DELETE、PATCH
- **状态码**：HTTP 响应状态码
- **版本控制**：API 版本管理

### 技术栈

- **FastAPI**：高性能 Web 框架
- **Pydantic**：数据验证和序列化
- **APIRouter**：路由分组

## 5.2 项目当前配置分析

### 目录结构

```
app/
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── api.py          # 路由注册
│       └── endpoints/      # API 端点
│           ├── __init__.py
│           ├── auth.py     # 认证相关
│           └── users.py    # 用户相关
├── schemas/
│   ├── __init__.py
│   ├── token.py           # Token 模型
│   └── user.py            # 用户模型
└── main.py                # 应用入口
```

## 5.3 RESTful API 设计原则

### 1. URL 设计规范

```python
# 好的设计
GET    /api/v1/users          # 获取用户列表
GET    /api/v1/users/{id}     # 获取单个用户
POST   /api/v1/users          # 创建用户
PUT    /api/v1/users/{id}     # 更新用户
DELETE /api/v1/users/{id}     # 删除用户

# 不好的设计
GET    /api/v1/getUsers       # 使用动词
POST   /api/v1/createUser     # 使用动词
GET    /api/v1/user/delete    # URL 中包含操作
```

### 2. HTTP 方法语义

| 方法 | 语义 | 幂等性 | 安全性 |
|------|------|--------|--------|
| GET | 获取资源 | 是 | 是 |
| POST | 创建资源 | 否 | 否 |
| PUT | 替换资源 | 是 | 否 |
| PATCH | 部分更新 | 否 | 否 |
| DELETE | 删除资源 | 是 | 否 |

### 3. 状态码使用规范

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器错误 |

## 5.4 RESTful API 实现步骤

### 步骤1：创建响应模型

**文件位置**：`app/schemas/base.py`

```python
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseBase(BaseModel, Generic[T]):
    """统一响应模型"""
    
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息")
    data: T | None = Field(None, description="数据")

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    
    items: list[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总数")
    page: int = Field(1, description="当前页")
    page_size: int = Field(10, description="每页数量")
    total_pages: int = Field(1, description="总页数")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    detail: Any | None = Field(None, description="详细信息")
```

**知识点**：
- 泛型模型：提高代码复用
- 统一响应格式：便于前端处理
- 分页响应：处理列表数据

### 步骤2：创建分页参数模型

**文件位置**：`app/schemas/pagination.py`

```python
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    """分页参数模型"""
    
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """计算限制数量"""
        return self.page_size

class SortParams(BaseModel):
    """排序参数模型"""
    
    sort_by: str = Field("id", description="排序字段")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="排序方式")
```

**知识点**：
- `Field` 验证：`ge`（大于等于）、`le`（小于等于）
- `pattern`：正则表达式验证
- `@property`：属性装饰器

### 步骤3：创建 CRUD 基类

**文件位置**：`app/crud/base.py`

```python
from typing import Any, Generic, TypeVar, Type
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class CRUDBase(Generic[ModelType]):
    """CRUD 基类"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """根据 ID 获取记录"""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ModelType], int]:
        """
        获取多条记录
        
        Returns:
            (记录列表, 总数)
        """
        query = select(self.model)
        
        # 应用过滤条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        # 应用分页
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = list(result.scalars().all())
        
        return items, total or 0
    
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
    
    async def get_by_field(
        self, db: AsyncSession, *, field: str, value: Any
    ) -> ModelType | None:
        """根据字段获取记录"""
        if not hasattr(self.model, field):
            return None
        result = await db.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()
```

**知识点**：
- 泛型 CRUD：通用的增删改查操作
- 分页查询：`offset` 和 `limit`
- 过滤条件：动态过滤
- 聚合查询：`func.count()`

### 步骤4：创建用户 CRUD

**文件位置**：`app/crud/user.py`

```python
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.user import User

class CRUDUser(CRUDBase[User]):
    """用户 CRUD 操作"""
    
    async def get_by_username(self, db: AsyncSession, *, username: str) -> User | None:
        """根据用户名获取用户"""
        return await self.get_by_field(db, field="username", value=username)
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """根据邮箱获取用户"""
        return await self.get_by_field(db, field="email", value=email)
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
        is_superuser: bool | None = None,
    ) -> tuple[list[User], int]:
        """获取用户列表"""
        filters = {
            "is_active": is_active,
            "is_superuser": is_superuser,
        }
        return await super().get_multi(
            db, skip=skip, limit=limit, filters=filters
        )
    
    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> User:
        """创建用户"""
        return await super().create(db, obj_in=obj_in)
    
    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: dict[str, Any]
    ) -> User:
        """更新用户"""
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)
    
    async def remove(self, db: AsyncSession, *, id: int) -> User | None:
        """删除用户"""
        return await super().remove(db, id=id)

# 创建用户 CRUD 实例
user_crud = CRUDUser(User)
```

### 步骤5：创建用户 Schema

**文件位置**：`app/schemas/user.py`

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")

class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=8, max_length=128, description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: str | None = Field(None, min_length=3, max_length=50, description="用户名")
    email: EmailStr | None = Field(None, description="邮箱")
    password: str | None = Field(None, min_length=8, max_length=128, description="密码")
    is_active: bool | None = Field(None, description="是否激活")

class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否管理员")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """用户列表响应模型"""
    items: list[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(1, description="当前页")
    page_size: int = Field(10, description="每页数量")
    total_pages: int = Field(1, description="总页数")
```

### 步骤6：创建用户路由

**文件位置**：`app/api/v1/endpoints/users.py`

```python
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user, get_current_superuser
from app.crud.user import user_crud
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from app.schemas.base import ResponseBase
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=ResponseBase[UserListResponse])
async def read_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: bool | None = Query(None, description="是否激活"),
):
    """
    获取用户列表（仅管理员）
    
    Args:
        db: 数据库会话
        current_user: 当前用户（管理员）
        page: 页码
        page_size: 每页数量
        is_active: 是否激活过滤
    
    Returns:
        用户列表响应
    """
    skip = (page - 1) * page_size
    users, total = await user_crud.get_multi(
        db,
        skip=skip,
        limit=page_size,
        is_active=is_active,
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return ResponseBase(
        data=UserListResponse(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    )

@router.get("/{user_id}", response_model=ResponseBase[UserResponse])
async def read_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    获取用户信息
    
    Args:
        user_id: 用户 ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        用户信息
    """
    # 普通用户只能查看自己的信息
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ResponseBase(data=UserResponse.model_validate(user))

@router.post("/", response_model=ResponseBase[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    创建用户
    
    Args:
        user_in: 用户创建数据
        db: 数据库会话
    
    Returns:
        创建的用户信息
    """
    # 检查用户名是否存在
    existing_user = await user_crud.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否存在
    existing_email = await user_crud.get_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建用户
    from app.core.security import get_password_hash
    user_data = user_in.model_dump()
    user_data["hashed_password"] = get_password_hash(user_in.password)
    del user_data["password"]
    
    user = await user_crud.create(db, obj_in=user_data)
    
    return ResponseBase(data=UserResponse.model_validate(user))

@router.put("/{user_id}", response_model=ResponseBase[UserResponse])
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    更新用户
    
    Args:
        user_id: 用户 ID
        user_in: 用户更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的用户信息
    """
    # 普通用户只能更新自己的信息
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 准备更新数据
    update_data = user_in.model_dump(exclude_unset=True)
    
    # 如果更新密码，进行哈希
    if "password" in update_data:
        from app.core.security import get_password_hash
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # 更新用户
    user = await user_crud.update(db, db_obj=user, obj_in=update_data)
    
    return ResponseBase(data=UserResponse.model_validate(user))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
):
    """
    删除用户（仅管理员）
    
    Args:
        user_id: 用户 ID
        db: 数据库会话
        current_user: 当前用户（管理员）
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    await user_crud.remove(db, id=user_id)
```

**知识点**：
- `Query`：查询参数验证
- `Depends`：依赖注入
- `status_code`：HTTP 状态码
- `model_validate`：模型验证
- `exclude_unset=True`：排除未设置的字段

### 步骤7：注册路由

**文件位置**：`app/api/v1/api.py`

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# 认证路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"],
    responses={401: {"description": "未授权"}},
)

# 用户路由
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户"],
    responses={404: {"description": "未找到"}},
)
```

### 步骤8：配置应用

**文件位置**：`app/main.py`

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.core.middleware import RequestLoggingMiddleware
from app.api.v1.api import api_router

settings = get_settings()

app = FastAPI(
    title=settings.TITLE,
    version=settings.VERSION,
    summary=settings.SUMMARY,
    description=settings.DESCRIPTION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    root_path=settings.ROOT_PATH,
    debug=settings.DEBUG,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 处理"""
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": "资源不存在",
            "detail": str(exc),
        },
    )

# 注册路由
app.include_router(api_router, prefix="/api/v1")

# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查"""
    return {"status": "ok"}
```

## 5.5 API 文档

### 1. Swagger UI

访问地址：`http://localhost:8001/docs`

功能：
- 自动生成 API 文档
- 在线测试 API
- 查看请求/响应模型

### 2. ReDoc

访问地址：`http://localhost:8001/redoc`

功能：
- 更美观的文档界面
- 支持搜索
- 支持导出

### 3. 自定义文档

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="""
    ## 用户管理 API
    
    这是一个用户管理系统的 API 文档。
    
    ### 功能特性
    
    - 用户注册和登录
    - 用户信息管理
    - 权限控制
    
    ### 联系方式
    
    - Email: admin@example.com
    """,
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Admin",
        "url": "http://example.com/contact/",
        "email": "admin@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
```

## 5.6 API 版本控制

### 1. URL 版本控制

```python
# app/api/v1/api.py
api_v1_router = APIRouter()

# app/api/v2/api.py
api_v2_router = APIRouter()

# app/main.py
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")
```

### 2. Header 版本控制

```python
from fastapi import APIRouter, Header

router = APIRouter()

@router.get("/users")
async def get_users(version: str = Header("v1")):
    if version == "v1":
        return get_users_v1()
    elif version == "v2":
        return get_users_v2()
```

## 5.7 最佳实践

### 1. 请求验证

```python
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("用户名必须是字母数字")
        return v
```

### 2. 响应模型

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    return {"name": "Foo", "price": 42.0}
```

### 3. 错误处理

```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
            headers={"X-Error": "Invalid item ID"},
        )
    return {"item_id": item_id}
```

## 5.8 常见问题

### Q1: 路由冲突

**原因**：
- 多个路由匹配同一 URL
- 路由顺序问题

**解决方案**：
```python
# 确保路由顺序正确
# 更具体的路由在前
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "current"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

### Q2: 跨域问题

**原因**：
- 前端和后端不在同一域名

**解决方案**：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q3: 请求体过大

**原因**：
- 默认请求体大小限制

**解决方案**：
```python
# Nginx 配置
client_max_body_size 100M;

# 或者使用流式处理
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename}
```

## 5.9 练习任务

### 任务1：创建文章 CRUD

实现完整的文章 CRUD API：
- `GET /api/v1/articles`：获取文章列表
- `GET /api/v1/articles/{id}`：获取文章详情
- `POST /api/v1/articles`：创建文章
- `PUT /api/v1/articles/{id}`：更新文章
- `DELETE /api/v1/articles/{id}`：删除文章

### 任务2：实现搜索功能

实现文章搜索 API：
- `GET /api/v1/articles/search?q=keyword`：搜索文章
- 支持分页
- 支持排序

### 任务3：实现文件上传

实现文件上传 API：
- `POST /api/v1/upload`：上传文件
- 支持多种文件类型
- 返回文件 URL

## 5.10 下一步学习

完成 RESTful API 开发后，下一步将学习：
- **测试框架**：单元测试和集成测试
- **性能优化**：缓存和数据库优化
- **部署上线**：Docker 容器化

---

**学习时间**：预计 4-6 小时

**难度级别**：⭐⭐⭐⭐☆