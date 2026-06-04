
import sys

from loguru import logger

from app.config.path_conf import LOG_DIR
from app.config.settings import setting
def setup_logger():
    """配置日志系统"""
    
    # 移除默认配置
    logger.remove()
    
    
    # 控制台处理器
    logger.add(
        sys.stdout,
        level=setting.LOGGER_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    
    # 文件处理器 - 所有日志
    logger.add(
        LOG_DIR / "app_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
               "{level: <8} | "
               "{name}:{function}:{line} | "
               "{message}",
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留 30 天
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
        enqueue=True,  # 异步写入
    )
    
    # 文件处理器 - 错误日志
    logger.add(
        LOG_DIR / "error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
               "{level: <8} | "
               "{name}:{function}:{line} | "
               "{message}",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
    )
    
    # 文件处理器 - 访问日志
    logger.add(
        LOG_DIR / "access_{time:YYYY-MM-DD}.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
               "{message}",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        filter=lambda record: "access" in record["extra"],
    )
    
    return logger

# 创建日志实例
app_logger = setup_logger()