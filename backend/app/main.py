import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn


# 将项目根目录加入 sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from app.config.settings import setting
from app.core.middleware import RequestLoggingMiddleware
from app.core.cors import setup_cros_middleware
from app.core.redis import redis_manager
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用生命周期"""
    # 启动：初始化 Redis
    if setting.REDIS.ENABLE:
        await redis_manager.init()
    yield
    # 关闭：清理资源
    if setting.REDIS.ENABLE:
        await redis_manager.close()


def create_app() -> FastAPI:
    """应用工厂函数"""
    app = FastAPI(
        title=setting.TITLE,
        version=setting.VERSION,
        summary=setting.SUMMARY,
        description=setting.DESCRIPTION,
        docs_url=setting.DOCS_URL,
        redoc_url=setting.REDOC_URL,
        root_path=setting.ROOT_PATH,
        debug=setting.DEBUG,
        lifespan=lifespan,
    )
    # 日志中间件
    app.add_middleware(RequestLoggingMiddleware)
    # 跨域处理
    setup_cros_middleware(app)
    app.include_router(api_router, prefix="/api/v1")

    return app


# 暴露 app 实例，供 uvicorn 直接引用：uvicorn app.main:app
app = create_app()


if __name__ == "__main__":
    # 直接运行：python app/main.py
    # 自动从 .env 配置文件读取 HOST / PORT / DEBUG
    uvicorn.run(
        "app.main:app",
        host=setting.SERVER_HOST,
        port=setting.SERVER_PORT,
        reload=setting.DEBUG,
        log_level="debug" if setting.DEBUG else "info",
    )
