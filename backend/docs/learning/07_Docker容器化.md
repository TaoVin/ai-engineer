# 步骤7：Docker 容器化

## 7.1 知识点概述

Docker 容器化是现代应用部署的标准方式，本节将学习如何将 FastAPI 应用容器化。

### 核心概念

- **容器（Container）**：轻量级的虚拟化技术
- **镜像（Image）**：容器的模板
- **Dockerfile**：构建镜像的脚本
- **Docker Compose**：多容器编排工具
- **卷（Volume）**：数据持久化

### 技术栈

- **Docker**：容器化平台
- **Docker Compose**：多容器编排
- **Nginx**：反向代理（可选）

## 7.2 项目当前配置分析

### 目录结构

```
docker/
├── Dockfile                # Dockerfile（注意拼写）
└── docker-compose.yml      # Docker Compose 配置
```

## 7.3 Docker 容器化实现步骤

### 步骤1：创建 Dockerfile

**文件位置**：`docker/Dockerfile`

```dockerfile
# 基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=prod

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN pip install poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 配置 Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 切换用户
USER appuser

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**知识点**：
- `FROM`：基础镜像
- `WORKDIR`：工作目录
- `ENV`：环境变量
- `RUN`：执行命令
- `COPY`：复制文件
- `USER`：运行用户
- `EXPOSE`：暴露端口
- `HEALTHCHECK`：健康检查
- `CMD`：启动命令

### 步骤2：创建 .dockerignore

**文件位置**：`.dockerignore`

```gitignore
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
.venv
venv/
ENV/

# IDE
.idea
.vscode
*.swp
*.swo

# 测试
.pytest_cache
.coverage
htmlcov/

# 日志
logs/
*.log

# 环境文件
.env.*
!.env.example

# Docker
docker/docker-compose.yml
docker/Dockerfile

# 文档
docs/
*.md
```

### 步骤3：创建 Docker Compose

**文件位置**：`docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  # FastAPI 应用
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: fastapi-app
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=prod
      - DATABASE_TYPE=mysql
      - DATABASE_HOST=mysql
      - DATABASE_PORT=3306
      - DATABASE_USER=root
      - DATABASE_PASSWORD=rootpassword
      - DATABASE_NAME=fastapi_db
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - app_logs:/app/logs
      - app_files:/app/files
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network

  # MySQL 数据库
  mysql:
    image: mysql:8.0
    container_name: fastapi-mysql
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=fastapi_db
      - MYSQL_USER=fastapi
      - MYSQL_PASSWORD=fastapi_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: fastapi-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Nginx 反向代理（可选）
  nginx:
    image: nginx:alpine
    container_name: fastapi-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - app-network

volumes:
  mysql_data:
  redis_data:
  app_logs:
  app_files:

networks:
  app-network:
    driver: bridge
```

**知识点**：
- `services`：服务定义
- `build`：构建配置
- `environment`：环境变量
- `volumes`：数据卷
- `depends_on`：依赖关系
- `healthcheck`：健康检查
- `networks`：网络配置

### 步骤4：创建 Nginx 配置

**文件位置**：`docker/nginx/nginx.conf`

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    # 访问日志
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 性能优化
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;

    # 上游服务器
    upstream fastapi {
        server app:8001;
    }

    server {
        listen 80;
        server_name localhost;

        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # 请求大小限制
        client_max_body_size 100M;

        # 静态文件
        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # API 代理
        location /api/ {
            proxy_pass http://fastapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 健康检查
        location /health {
            proxy_pass http://fastapi;
            access_log off;
        }

        # 文档
        location /docs {
            proxy_pass http://fastapi;
        }

        location /redoc {
            proxy_pass http://fastapi;
        }

        # 默认路由
        location / {
            proxy_pass http://fastapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 步骤5：创建环境配置文件

**文件位置**：`docker/.env.example`

```bash
# 环境配置
ENVIRONMENT=prod

# 数据库配置（MySQL）
DATABASE_TYPE=mysql
DATABASE_HOST=mysql
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_secure_password
DATABASE_NAME=fastapi_db

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# 应用配置
SECRET_KEY=your_secret_key_here
SERVER_HOST=0.0.0.0
SERVER_PORT=8001

# 日志配置
LOGGER_LEVEL=INFO
```

### 步骤6：创建 Makefile

**文件位置**：`Makefile`

```makefile
.PHONY: help build up down restart logs clean test

# 默认目标
help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker 命令
build: ## 构建镜像
	docker-compose -f docker/docker-compose.yml build

up: ## 启动服务
	docker-compose -f docker/docker-compose.yml up -d

down: ## 停止服务
	docker-compose -f docker/docker-compose.yml down

restart: ## 重启服务
	docker-compose -f docker/docker-compose.yml restart

logs: ## 查看日志
	docker-compose -f docker/docker-compose.yml logs -f

logs-app: ## 查看应用日志
	docker-compose -f docker/docker-compose.yml logs -f app

logs-db: ## 查看数据库日志
	docker-compose -f docker/docker-compose.yml logs -f mysql

ps: ## 查看服务状态
	docker-compose -f docker/docker-compose.yml ps

# 开发命令
dev: ## 启动开发环境
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d

dev-down: ## 停止开发环境
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml down

# 测试命令
test: ## 运行测试
	docker-compose -f docker/docker-compose.yml exec app pytest

test-cov: ## 运行测试并生成覆盖率报告
	docker-compose -f docker/docker-compose.yml exec app pytest --cov=app --cov-report=html

# 数据库命令
db-migrate: ## 运行数据库迁移
	docker-compose -f docker/docker-compose.yml exec app alembic upgrade head

db-revision: ## 创建数据库迁移
	docker-compose -f docker/docker-compose.yml exec app alembic revision --autogenerate -m "$(msg)"

db-reset: ## 重置数据库
	docker-compose -f docker/docker-compose.yml exec app alembic downgrade base
	docker-compose -f docker/docker-compose.yml exec app alembic upgrade head

# 清理命令
clean: ## 清理未使用的资源
	docker system prune -f
	docker volume prune -f

clean-all: ## 清理所有资源
	docker system prune -af
	docker volume prune -f

# 部署命令
deploy: ## 部署到生产环境
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d --build

deploy-down: ## 停止生产环境
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml down
```

### 步骤7：创建开发环境配置

**文件位置**：`docker/docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    environment:
      - ENVIRONMENT=dev
      - DEBUG=True
    volumes:
      - ../app:/app/app
      - ../logs:/app/logs
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

  mysql:
    ports:
      - "3306:3306"

  redis:
    ports:
      - "6379:6379"
```

### 步骤8：创建生产环境配置

**文件位置**：`docker/docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  app:
    environment:
      - ENVIRONMENT=prod
      - DEBUG=False
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s

  nginx:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.25'
          memory: 128M
```

## 7.4 Docker 命令

### 1. 镜像管理

```bash
# 构建镜像
docker build -t fastapi-app .

# 查看镜像
docker images

# 删除镜像
docker rmi fastapi-app

# 清理未使用的镜像
docker image prune
```

### 2. 容器管理

```bash
# 运行容器
docker run -d -p 8001:8001 --name fastapi-app fastapi-app

# 查看容器
docker ps

# 停止容器
docker stop fastapi-app

# 启动容器
docker start fastapi-app

# 重启容器
docker restart fastapi-app

# 删除容器
docker rm fastapi-app

# 查看容器日志
docker logs fastapi-app

# 进入容器
docker exec -it fastapi-app bash
```

### 3. Docker Compose 命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重新构建并启动
docker-compose up -d --build

# 执行命令
docker-compose exec app python -m pytest
```

## 7.5 最佳实践

### 1. 多阶段构建

```dockerfile
# 构建阶段
FROM python:3.13-slim as builder

WORKDIR /app

# 安装 Poetry
RUN pip install poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# 运行阶段
FROM python:3.13-slim

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. 安全最佳实践

```dockerfile
# 使用非 root 用户
RUN useradd -m -u 1000 appuser
USER appuser

# 只读文件系统
docker run --read-only fastapi-app

# 限制资源
docker run --memory=512m --cpus=0.5 fastapi-app
```

### 3. 镜像优化

```dockerfile
# 使用 slim 镜像
FROM python:3.13-slim

# 合并 RUN 命令
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 使用 .dockerignore
# 减少镜像层数
```

### 4. 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1
```

## 7.6 常见问题

### Q1: 构建失败

**原因**：
- 依赖安装失败
- 网络问题

**解决方案**：
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者使用代理
docker build --build-arg http_proxy=http://proxy:8080 .
```

### Q2: 容器无法启动

**原因**：
- 端口冲突
- 配置错误

**解决方案**：
```bash
# 检查端口占用
netstat -tulpn | grep 8001

# 查看容器日志
docker logs fastapi-app

# 检查配置
docker-compose config
```

### Q3: 数据库连接失败

**原因**：
- 数据库未启动
- 连接参数错误

**解决方案**：
```bash
# 检查数据库状态
docker-compose ps mysql

# 查看数据库日志
docker-compose logs mysql

# 测试连接
docker-compose exec app python -c "import aiomysql; print('MySQL driver OK')"
```

### Q4: 性能问题

**原因**：
- 资源限制过严
- 配置不当

**解决方案**：
```yaml
# 调整资源限制
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1024M
```

## 7.7 练习任务

### 任务1：配置 SSL

配置 Nginx 使用 SSL 证书。

### 任务2：配置日志收集

配置 ELK 或 Loki 收集容器日志。

### 任务3：配置监控

配置 Prometheus 和 Grafana 监控容器。

## 7.8 下一步学习

完成 Docker 容器化后，下一步将学习：
- **CI/CD**：持续集成和部署
- **云部署**：部署到云平台
- **微服务**：服务拆分和治理

---

**学习时间**：预计 3-5 小时

**难度级别**：⭐⭐⭐☆☆