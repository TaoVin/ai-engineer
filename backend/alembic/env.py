from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from app.config.settings import setting
from alembic import context
import asyncio

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.models.base import Base
# 导入所有模型，确保它们被注册到 Base.metadata
from app.models.user import User  # noqa: F401

target_metadata = Base.metadata

# 获取数据库 URL
DATABASE_URL = setting.DATABASE.DB_URI
if DATABASE_URL.startswith("mysql+aiomysql"):
    # 转换为同步URL
    DATABASE_URL = DATABASE_URL.replace("mysql+aiomysql", "mysql+pymysql")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """执行迁移"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        transaction_per_migration=False
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode (异步)."""
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        # 确保提交事务
        await connection.commit()

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
