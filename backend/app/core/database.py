from click import echo
from sqlalchemy import engine

from app.config.settings import setting
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DB_CONFIG = setting.DATABASE


# 创建异步引擎

engine = create_async_engine(
    DB_CONFIG.DB_URI,
    echo=setting.DATABASE_ECHO,
    echo_pool=setting.ECHO_POOL,
    pool_size=setting.POOL_SIZE,
    max_overflow=setting.MAX_OVERFLOW,
    pool_timeout=setting.POOL_TIMEOUT,
    pool_recycle=setting.POOL_RECYCLE,
    pool_use_lifo=setting.POOL_USE_LIFO,
    pool_pre_ping=setting.POOL_PRE_PING,
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=setting.EXPIRE_ON_COMMIT,
    autoflush=setting.AUTOFETCH,
    autocommit=setting.AUTOCOMMIT
)