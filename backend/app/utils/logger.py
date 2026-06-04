import functools
import time
from typing import Any, Callable
from loguru import logger


def log_execution(func: Callable) -> Callable:
    """
    记录函数执行的装饰器

    Args:
        func: 被装饰的函数

    Returns:
        装饰后的函数
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"开始执行: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"执行完成: {func.__name__} | " f"耗时: {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"执行失败: {func.__name__} | "
                f"错误: {str(e)} | "
                f"耗时: {execution_time:.3f}s"
            )
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"开始执行: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"执行完成: {func.__name__} | " f"耗时: {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"执行失败: {func.__name__} | "
                f"错误: {str(e)} | "
                f"耗时: {execution_time:.3f}s"
            )
            raise

    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def log_request(request_data: dict[str, Any]) -> None:
    """
    记录请求信息

    Args:
        request_data: 请求数据
    """
    logger.bind(access=True).info(
        f"请求: {request_data.get('method')} {request_data.get('url')} | "
        f"客户端: {request_data.get('client_ip')} | "
        f"状态码: {request_data.get('status_code')} | "
        f"耗时: {request_data.get('duration', 0):.3f}s"
    )


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """
    记录错误信息

    Args:
        error: 异常对象
        context: 上下文信息
    """
    error_info = {
        "type": type(error).__name__,
        "message": str(error),
        "context": context or {},
    }
    logger.error(f"错误: {error_info}")


def log_database_query(
    query: str, params: dict[str, Any] | None = None, duration: float = 0
) -> None:
    """
    记录数据库查询

    Args:
        query: SQL 查询
        params: 查询参数
        duration: 执行时间
    """
    logger.debug(
        f"数据库查询: {query} | " f"参数: {params} | " f"耗时: {duration:.3f}s"
    )
