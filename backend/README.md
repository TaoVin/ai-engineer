# FastAPI Admin

基于 **FastAPI + SQLAlchemy 2.0 + MySQL + Redis + OpenAI** 构建的 AI 应用后台管理系统。

## 项目概述

FastAPI Admin 是一个学习实战项目，集成了完整的 RBAC 权限管理系统和 LLM 聊天功能。项目采用现代化的 Python 异步技术栈，提供了用户管理、角色管理、权限管理、AI 流式聊天等核心功能。

## 技术栈

| 分类 | 技术 | 用途 |
|------|------|------|
| 框架 | FastAPI | Web 框架 |
| ASGI 服务器 | Uvicorn / Gunicorn | 开发/生产服务器 |
| ORM | SQLAlchemy 2.0 | 对象关系映射 |
| 数据库 | MySQL 8.0+ | 关系型数据库 |
| 异步驱动 | aiomysql | MySQL 异步连接 |
| 缓存 | Redis | 会话/验证码/缓存 |
| 迁移 | Alembic | 数据库版本管理 |
| 认证 | JWT (python-jose) + bcrypt | 用户认证 |
| AI | OpenAI API 兼容接口 | AI 聊天 |
| 流式响应 | SSE (sse-starlette) | 流式聊天 |
| 日志 | Loguru | 日志记录 |
| 配置 | Pydantic Settings | 环境配置管理 |
| 包管理 | Poetry | 依赖管理 |
| 代码质量 | Ruff / Black / MyPy | 代码检查与格式化 |
| 测试 | Pytest | 单元测试 |

## 快速开始

### 前置条件

- Python 3.13+
- MySQL 8.0+
- Redis 7.0+
- Poetry

### 1. 克隆项目

```bash
git clone <repository-url>
cd backend
```

### 2. 安装依赖

```bash
# 安装 Poetry（如未安装）
pip install poetry

# 安装项目依赖
poetry install
```

### 3. 配置环境变量

```bash
# 复制开发环境配置
cp .env.dev .env

# 根据需要修改配置
# 主要配置项：
# - DATABASE_HOST / DATABASE_PORT / DATABASE_USER / DATABASE_PASSWORD / DATABASE_NAME
# - REDIS_HOST / REDIS_PORT
# - OPENAI_BASE_URL / OPENAI_API_KEY / OPENAI_MODEL
```

### 4. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS fastapi-test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行数据库迁移
bash scripts/dbupgrade.sh
```

### 5. 启动服务

```bash
# 开发环境（热重载）
bash scripts/start.sh dev

# 生产环境
bash scripts/start.sh prod
```

服务启动后访问：
- API 文档：http://localhost:8001/docs
- ReDoc：http://localhost:8001/redoc
- API 根路径：http://localhost:8001/api/v1

## 项目结构

```
backend/
├── app/                        # 应用主代码
│   ├── api/v1/endpoints/       # API 路由
│   │   ├── llm/chat.py         # AI 聊天接口
│   │   └── system/             # 系统管理接口
│   │       ├── auth.py         # 认证
│   │       ├── users.py        # 用户管理
│   │       ├── roles.py        # 角色管理
│   │       └── permission.py   # 权限管理
│   ├── core/                   # 核心模块
│   │   ├── database.py         # 数据库连接
│   │   ├── security.py         # JWT + 密码哈希
│   │   ├── redis.py            # Redis 客户端
│   │   ├── openai.py           # OpenAI 客户端 + 流式响应
│   │   ├── deps.py             # 依赖注入
│   │   ├── exception.py        # 全局异常处理
│   │   └── middleware.py       # 请求日志中间件
│   ├── models/                 # ORM 数据模型
│   │   ├── base.py             # 基类（主键/时间戳/审计字段/逻辑删除）
│   │   ├── llm/chat.py         # 聊天模型
│   │   └── system/             # 系统管理模型
│   ├── schemas/                # Pydantic 数据校验
│   │   ├── base.py             # 统一响应/分页
│   │   ├── llm/chat.py         # 聊天 Schema
│   │   └── system/             # 系统管理 Schema
│   ├── service/                # 业务逻辑层
│   │   ├── llm/chat_service.py # 聊天服务
│   │   └── system/             # 系统管理服务
│   ├── mapper/                 # 数据访问层
│   │   ├── base.py             # CRUD 泛型基类
│   │   ├── llm/chat_mapper.py  # 聊天数据访问
│   │   └── system/             # 系统管理数据访问
│   ├── enums/                  # 枚举定义
│   ├── config/                 # 配置管理
│   └── main.py                 # 应用入口
├── alembic/                    # 数据库迁移
├── scripts/                    # 启动/管理脚本
├── docs/learning/              # 学习文档
├── docker/                     # Docker 配置（待完善）
├── .env.dev                    # 开发环境配置
├── .env.prod                   # 生产环境配置
├── pyproject.toml              # 项目配置
└── README.md                   # 项目文档
```

## 配置说明

### 环境管理

项目支持 `dev`（开发）和 `prod`（生产）两种环境，通过 `.env.dev` 和 `.env.prod` 文件配置。

### 核心配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | `dev` |
| `SERVER_HOST` | 服务监听地址 | `localhost` |
| `SERVER_PORT` | 服务端口 | `8001` |
| `DATABASE_TYPE` | 数据库类型 | `mysql` |
| `DATABASE_HOST` | 数据库地址 | `localhost` |
| `DATABASE_PORT` | 数据库端口 | `3306` |
| `DATABASE_NAME` | 数据库名称 | `fastapi-test` |
| `REDIS_ENABLE` | 是否启用 Redis | `True` |
| `REDIS_HOST` | Redis 地址 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `SECRET_KEY` | JWT 加密密钥 | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 过期时间（天） | `7` |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址 | `https://api.deepseek.com` |
| `OPENAI_API_KEY` | API 密钥 | — |
| `OPENAI_MODEL` | 模型名称 | `deepseek-v4-flash` |

## API 接口

### 认证管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/sys/auth/code` | 获取验证码 |
| POST | `/api/v1/sys/auth/login` | 登录 |
| POST | `/api/v1/sys/auth/refresh` | 刷新 Token |
| GET | `/api/v1/sys/auth/me` | 获取当前用户信息 |

### 用户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/sys/users/create` | 创建用户 |
| DELETE | `/api/v1/sys/users/delete/{ids}` | 删除用户（批量） |
| POST | `/api/v1/sys/users/update` | 更新用户 |
| GET | `/api/v1/sys/users/query/pages` | 用户分页查询 |
| GET | `/api/v1/sys/users/query/{id}` | 用户详情 |
| GET | `/api/v1/sys/users/query/byName` | 根据用户名查询 |
| POST | `/api/v1/sys/users/bindRole` | 绑定角色 |
| DELETE | `/api/v1/sys/users/unbindRole/{id}` | 解绑角色 |
| POST | `/api/v1/sys/users/resetPwd` | 重置密码 |

### 角色管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/sys/roles/create` | 创建角色 |
| DELETE | `/api/v1/sys/roles/delete/{ids}` | 删除角色（批量） |
| POST | `/api/v1/sys/roles/update` | 更新角色 |
| GET | `/api/v1/sys/roles/query/pages` | 角色分页查询 |
| GET | `/api/v1/sys/roles/query/{id}` | 角色详情 |
| POST | `/api/v1/sys/roles/bindPermission` | 绑定权限 |
| DELETE | `/api/v1/sys/roles/unbindPermission/{id}` | 解绑权限 |

### 权限管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/sys/permission/create` | 创建权限 |
| DELETE | `/api/v1/sys/permission/delete/{ids}` | 删除权限（批量） |
| POST | `/api/v1/sys/permission/update` | 更新权限 |
| GET | `/api/v1/sys/permission/query/pages` | 权限分页查询 |
| GET | `/api/v1/sys/permission/query/{id}` | 权限详情 |

### AI 聊天

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/ai/chat/stream` | 流式聊天（SSE） |
| POST | `/api/v1/ai/chat/sessions` | 获取会话列表 |
| GET | `/api/v1/ai/chat/sessions/{session_id}` | 获取会话详情 |
| PUT | `/api/v1/ai/chat/sessions/rename` | 重命名会话 |

## 数据库模型

### 系统管理

```
sys_user           - 用户表（用户名、昵称、邮箱、密码）
sys_role           - 角色表（角色名、角色键值、描述、排序）
sys_permission     - 权限表（权限名、父级ID、权限标识、类型、路径）
sys_user_role      - 用户-角色关联表（多对多）
sys_role_permission - 角色-权限关联表（多对多）
```

### LLM 聊天

```
chat_session       - 聊天会话表（会话ID、名称、最后活跃时间）
chat_message       - 聊天消息表（会话ID、内容、角色、名称、工具调用ID）
```

### 共有字段

所有表继承自 `BaseModel`，自动包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer (PK) | 主键，自增 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |
| `created_id` | Integer (FK) | 创建者 ID |
| `updated_id` | Integer (FK) | 更新者 ID |

部分继承LogicDeleteMixin，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `is_deleted` | Boolean | 逻辑删除标记 |
| `deleted_at` | DateTime | 删除时间 |
| `deleted_id` | Integer (FK) | 删除者 ID |

## 认证流程

### 登录流程

1. 客户端获取验证码（`GET /auth/code`）
2. 客户端提交用户名、密码、验证码（`POST /auth/login`）
3. 服务端验证验证码 → 验证用户密码 → 生成 JWT Token（access_token + refresh_token）
4. 客户端使用 access_token 在请求头 `Authorization: Bearer <token>` 访问受保护接口

### Token 刷新

当 access_token 过期时，使用 refresh_token 获取新的 access_token（`POST /auth/refresh`）。

## 开发指南

### 代码规范

```bash
# 格式化代码
black app/

# 代码检查
ruff check app/

# 类型检查
mypy app/
```

### 数据库迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "迁移说明"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

### 添加新功能

1. 定义 ORM 模型（`app/models/`）
2. 创建 Pydantic Schema（`app/schemas/`）
3. 实现 Mapper 数据访问（`app/mapper/`）
4. 编写 Service 业务逻辑（`app/service/`）
5. 创建 API 端点（`app/api/v1/endpoints/`）
6. 生成数据库迁移
7. 编写单元测试

## 部署

### Docker 部署（待完善）

```bash
# 构建镜像
docker build -f docker/Dockerfile -t fastapi-admin .

# 运行容器
docker run -d \
  --name fastapi-admin \
  -p 8001:8001 \
  --env-file .env.prod \
  fastapi-admin
```

### 直接部署

```bash
# 生产环境启动
bash scripts/start.sh prod
```

生产环境使用 Gunicorn + Uvicorn Worker 多进程模式，自动根据 CPU 核心数调整 Worker 数量。

## 常见问题

### 数据库连接失败

检查 `.env` 配置文件中的数据库连接信息是否正确，确认 MySQL 服务是否正常运行。

### Redis 连接失败

如不使用 Redis，可将 `REDIS_ENABLE` 设为 `False`。如需使用，确认 Redis 服务是否正常运行。

### 迁移执行失败

```bash
# 回滚到初始状态后重新执行迁移
alembic downgrade base
alembic upgrade head
```

## 学习资源

项目 `docs/learning/` 目录包含了从零搭建本项目的完整学习文档：

1. [配置管理](docs/learning/01_配置管理.md)
2. [数据库集成](docs/learning/02_数据库集成.md)
3. [用户认证](docs/learning/03_用户认证.md)
4. [日志系统](docs/learning/04_日志系统.md)
5. [RESTful API 开发](docs/learning/05_RESTful_API开发.md)
6. [测试框架](docs/learning/06_测试框架.md)
7. [Docker 容器化](docs/learning/07_Docker容器化.md)
8. [项目启动配置](docs/learning/08_项目启动配置.md)

## 许可证

MIT License
