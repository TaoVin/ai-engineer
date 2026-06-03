from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory

'''
AsyncGenerator：异步生成器类型
async with：异步上下文管理器
yield：依赖注入中的会话提供
commit()：提交事务
rollback()：回滚事务
close()：关闭会话
'''
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """ 获取数据库会话 """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
    