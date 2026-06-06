# 读取系统配置

import os
from enum import Enum
from functools import lru_cache
from typing import Literal
from pydantic import BaseModel, Field, SecretStr, computed_field, field_validator, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
from app.config.path_conf import BASE_DIR

# 环境变量枚举
class Environment(str, Enum):
    """环境枚举"""
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    
# mysql 数据库配置
class DatabaseConfig(BaseModel):
      # 数据库配置
    TYPE: str = (
        "mysql"  # mysql、postgres、sqlite、dm(sqlite、dm不支持代码生成)
    )

    # 数据库配置
    
    HOST: str = "localhost"
    PORT: int = 3306  # MySQL:3306 PostgreSQL:5432
    USER: str = "root"
    PASSWORD: SecretStr = SecretStr("")
    NAME: str = "test"
    
    # computed_field 将计算结果包含在序列化输出中
    @property
    def DB_URI(self) -> str:
        """
        同步 SQLAlchemy 数据库 URL。

        返回:
        - str: 同步驱动连接串。

        异常:
        - ValueError: 数据库类型不支持时抛出。
        """
        if self.TYPE not in ("mysql", "postgres", "sqlite"):
            raise ValueError(
                f"数据库驱动不支持: {self.TYPE}, 同步数据库请选择 mysql、postgres、sqlite"
            )
        db_connect: str = ""
        if self.TYPE == "mysql":
            # quote_plus 处理url拼接中的特殊字符
            db_connect = f"mysql+aiomysql://{self.USER}:{quote_plus(self.PASSWORD.get_secret_value())}@{self.HOST}:{self.PORT}/{self.NAME}?charset=utf8mb4"
        elif self.TYPE == "postgres":
            db_connect = f"postgresql+psycopg://{self.TYPE}:{quote_plus(self.PASSWORD.get_secret_value())}@{self.HOST}:{self.PORT}/{self.NAME}"
        else:
            db_connect = f"sqlite:///{self.NAME}.db"
        return db_connect


# redis 配置
class RedisConfig(BaseModel):
    """Redis 配置"""
    ENABLE: bool = True
    HOST: str = "localhost"
    PORT: int = 6379
    USER: str = ""
    PASSWORD: str = ""
    DB_NAME: int = 1
    KEY_PREFIX: str = "fastapi:"  # 全局键前缀
    SOCKET_TIMEOUT: int = 5  # 套接字超时(秒)
    SOCKET_CONNECT_TIMEOUT: int = 3  # 连接超时(秒)
    RETRY_ON_TIMEOUT: bool = True  # 超时是否重试
    MAX_CONNECTIONS: int = 20  # 连接池最大连接数
    HEALTH_CHECK_INTERVAL: int = 10  # 健康检查间隔(秒)




class Setting(BaseSettings):

    # 读取环境
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / f".env.{os.getenv('ENVIRONMENT', 'dev')}",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,  # 区分大小写
        env_nested_delimiter="_"
    )
  
    # 默认开发环境 
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT)

    # 服务器配置
    SERVER_HOST: str = "localhost"  # 允许访问的IP地址
    SERVER_PORT: int = 8001  # 服务端口

    # 文档配置
    DEBUG: bool = True  # 调试模式
    TITLE: str = "🎉 FastapiAdmin 🎉 -dev"  # 文档标题
    VERSION: str = "0.1.0"  # 版本号
    SUMMARY: str = "接口汇总"  # 文档概述
    DOCS_URL: str = "/docs"  # Swagger UI路径
    REDOC_URL: str = "/redoc"  # ReDoc路径
    ROOT_PATH: str = "/api/v1"  # API路由前缀
    DESCRIPTION: str = (
        "该项目是一个基于python的web服务框架，基于fastapi和sqlalchemy实现。"  # 文档描述
    )

    # 是否启用演示模式
    DEMO_ENABLE: bool = False
    
    # redis配置
    REDIS: RedisConfig = RedisConfig()
    
    
    # ================================================= #
    # ******************** 数据库配置 ******************* #
    # ================================================= #
    SQL_DB_ENABLE: bool = True  # 是否启用数据库
    DATABASE_ECHO: bool | Literal["debug"] = False  # 是否显示SQL日志
    ECHO_POOL: bool | Literal["debug"] = False  # 是否显示连接池日志
    POOL_SIZE: int = 10  # 连接池大小
    MAX_OVERFLOW: int = 20  # 最大溢出连接数
    POOL_TIMEOUT: int = 30  # 连接超时时间(秒)
    POOL_RECYCLE: int = 1800  # 连接回收时间(秒)
    POOL_USE_LIFO: bool = True  # 是否使用LIFO连接池
    POOL_PRE_PING: bool = True  # 是否开启连接预检
    FUTURE: bool = True  # 是否使用SQLAlchemy 2.0特性
    AUTOCOMMIT: bool = False  # 是否自动提交
    AUTOFETCH: bool = False  # 是否自动刷新
    EXPIRE_ON_COMMIT: bool = False  # 是否在提交时过期
    
    # 数据库配置
    DATABASE: DatabaseConfig = DatabaseConfig()
    
    # 日志配置
    LOGGER_LEVEL: str = "DEBUG"  # 日志级别

    # 大模型配置
    OPENAI_BASE_URL: str = "https://api.deepseek.com"
    OPENAI_API_KEY: str = "your_api_key"
    OPENAI_MODEL: str = "deepseek-v4-flash"

    # IP 归属地查询（登录时对外请求第三方 API，生产建议关闭）
    IP_LOCATION_ENABLE: bool = False
    
    # 安全认证配置
    # 加密密钥
    SECURITY_KEY: SecretStr = SecretStr("")
    # token 过期时间 分钟
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # token 刷新时间 天
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    
    DEFAULT_PWD: SecretStr = SecretStr("")
    
    # 校验配置参数
    @field_validator("SERVER_PORT")
    def validate_port(cls, v):
        if not 1024 <= v <= 65535:
            raise ValueError("端口必须在 1024-65535 之间")
        return v
    

@lru_cache(maxsize=1)
def get_settings() -> Setting:
    return Setting()



#创建配置的缓存
setting = get_settings();
