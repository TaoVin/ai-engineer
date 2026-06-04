# FastAPI 项目搭建学习指南

## 项目概述

这是一个基于 FastAPI 的 Web 服务框架学习项目，使用 SQLAlchemy 2.0 + Alembic 进行数据库管理，采用 JWT 进行用户认证。

## 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.13+ | 编程语言 |
| FastAPI | 0.136.3+ | Web 框架 |
| SQLAlchemy | 2.0.50+ | ORM 框架 |
| Alembic | 1.18.4+ | 数据库迁移 |
| MySQL | 8.0+ | 数据库 |
| Redis | 7 | 缓存 |
| JWT | - | 用户认证 |
| pytest | 9.0.3+ | 测试框架 |
| Docker | 24+ | 容器化 |

## 学习路线

按照以下顺序学习，每个步骤都有对应的详细文档：

### 步骤1：配置管理
- **难度**：⭐⭐☆☆☆
- **时间**：2-3 小时
- **内容**：Pydantic Settings、环境变量管理、多环境配置
- **文档**：[01_配置管理.md](01_配置管理.md)

### 步骤2：数据库集成
- **难度**：⭐⭐⭐☆☆
- **时间**：4-6 小时
- **内容**：SQLAlchemy 2.0、异步数据库操作、Alembic 迁移
- **文档**：[02_数据库集成.md](02_数据库集成.md)

### 步骤3：用户认证
- **难度**：⭐⭐⭐⭐☆
- **时间**：3-5 小时
- **内容**：JWT Token、密码哈希、OAuth2、权限控制
- **文档**：[03_用户认证.md](03_用户认证.md)

### 步骤4：日志系统
- **难度**：⭐⭐☆☆☆
- **时间**：2-3 小时
- **内容**：loguru、结构化日志、日志轮转、中间件
- **文档**：[04_日志系统.md](04_日志系统.md)

### 步骤5：RESTful API 开发
- **难度**：⭐⭐⭐⭐☆
- **时间**：4-6 小时
- **内容**：路由设计、数据验证、响应模型、错误处理
- **文档**：[05_RESTful_API开发.md](05_RESTful_API开发.md)

### 步骤6：测试框架
- **难度**：⭐⭐⭐☆☆
- **时间**：3-5 小时
- **内容**：pytest、异步测试、测试覆盖、Mock
- **文档**：[06_测试框架.md](06_测试框架.md)

### 步骤7：Docker 容器化
- **难度**：⭐⭐⭐☆☆
- **时间**：3-5 小时
- **内容**：Dockerfile、Docker Compose、Nginx、生产部署
- **文档**：[07_Docker容器化.md](07_Docker容器化.md)

### 步骤8：项目启动配置
- **难度**：⭐⭐⭐☆☆
- **时间**：2-3 小时
- **内容**：ASGI 协议、Uvicorn 服务器、应用工厂模式、Gunicorn 生产部署、生命周期事件
- **文档**：[08_项目启动配置.md](08_项目启动配置.md)

## 学习建议

1. **循序渐进**：按照步骤顺序学习，每个步骤都要动手实践
2. **理解原理**：不要只是复制代码，要理解每个概念的原理
3. **多做练习**：每个文档都有练习任务，尽量完成
4. **查阅文档**：遇到问题时，查阅官方文档
5. **代码审查**：完成代码后，进行自我审查

## 项目结构

```
backend/
├── app/                    # 应用代码
│   ├── api/                # API 路由
│   │   └── v1/             # API v1 版本
│   │       ├── api.py      # 路由注册
│   │       └── endpoints/  # API 端点
│   ├── config/             # 配置管理
│   │   ├── settings.py     # 配置类
│   │   └── path_conf.py    # 路径配置
│   ├── core/               # 核心模块
│   │   ├── database.py     # 数据库引擎
│   │   ├── security.py     # 安全相关
│   │   └── deps.py         # 依赖注入
│   ├── crud/               # CRUD 操作
│   ├── models/             # 数据库模型
│   ├── schemas/            # Pydantic 模型
│   ├── utils/              # 工具函数
│   └── tests/              # 测试代码
├── alembic/                # 数据库迁移
├── docker/                 # Docker 配置
├── docs/                   # 文档
│   └── learning/           # 学习文档
├── logs/                   # 日志文件
├── files/                  # 上传文件
├── pyproject.toml          # 项目配置
├── poetry.lock             # 依赖锁定
└── .env.*                  # 环境配置
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 Poetry
poetry install

# 或者使用 pip
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境配置
cp .env.example .env.dev

# 修改配置
vim .env.dev
```

### 3. 初始化数据库

```bash
# 运行迁移
alembic upgrade head
```

### 4. 启动应用

```bash
# 开发模式
uvicorn app.main:app --reload

# 或者使用 Makefile
make dev
```

### 5. 访问文档

- Swagger UI：http://localhost:8001/docs
- ReDoc：http://localhost:8001/redoc

## 常用命令

```bash
# 开发
make dev                # 启动开发环境
make dev-down           # 停止开发环境

# 测试
make test               # 运行测试
make test-cov           # 运行测试并生成覆盖率报告

# 数据库
make db-migrate         # 运行迁移
make db-revision msg="描述"  # 创建迁移
make db-reset           # 重置数据库

# Docker
make build              # 构建镜像
make up                 # 启动服务
make down               # 停止服务
make logs               # 查看日志

# 清理
make clean              # 清理未使用的资源
make clean-all           # 清理所有资源
```

## 学习资源

### 官方文档
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [pytest](https://docs.pytest.org/)
- [Docker](https://docs.docker.com/)

### 推荐阅读
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

## 常见问题

### Q1: 如何选择数据库？
- **MySQL**：广泛使用，社区活跃，适合大多数场景
- **PostgreSQL**：功能强大，支持异步，适合复杂查询
- **SQLite**：开发测试用，不适合生产

### Q2: 如何选择认证方式？
- **JWT**：无状态，适合 API
- **Session**：有状态，适合传统 Web
- **OAuth2**：第三方登录

### Q3: 如何部署到生产环境？
- 使用 Docker 容器化
- 配置 Nginx 反向代理
- 使用 CI/CD 自动部署
- 配置监控和告警

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License

---

**祝你学习愉快！**