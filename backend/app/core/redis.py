"""Redis 工具类

封装常用的 Redis 操作，支持:
- JSON 自动序列化/反序列化
- 全局键前缀
- 连接池管理
- 常用数据类型操作
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis

from app.config.settings import setting
from app.utils.logger import logger


class RedisManager:
    """Redis 操作封装"""

    def __init__(self):
        cfg = setting.REDIS
        self._enable = cfg.ENABLE
        self._prefix = cfg.KEY_PREFIX
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None

    # ──────────────────── 生命周期 ────────────────────

    async def init(self) -> None:
        """初始化连接池（应用启动时调用）"""
        if not self._enable:
            logger.warning("Redis 未启用，跳过初始化")
            return

        cfg = setting.REDIS
        self._pool = ConnectionPool.from_url(
            f"redis://{cfg.HOST}:{cfg.PORT}/{cfg.DB_NAME}",
            password=cfg.PASSWORD or None,
            decode_responses=True,
            socket_timeout=cfg.SOCKET_TIMEOUT,
            socket_connect_timeout=cfg.SOCKET_CONNECT_TIMEOUT,
            retry_on_timeout=cfg.RETRY_ON_TIMEOUT,
            max_connections=cfg.MAX_CONNECTIONS,
            health_check_interval=cfg.HEALTH_CHECK_INTERVAL,
        )
        self._client = Redis(connection_pool=self._pool)

        try:
            await self._client.ping()
            logger.info("Redis 连接成功 [{}:{}] db={}", cfg.HOST, cfg.PORT, cfg.DB_NAME)
        except Exception as e:
            logger.error("Redis 连接失败: {}", e)
            await self.close()
            raise

    async def close(self) -> None:
        """关闭连接池（应用关闭时调用）"""
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._pool:
            await self._pool.aclose()
            self._pool = None
        logger.info("Redis 连接已关闭")

    @property
    def client(self) -> Redis:
        if not self._client:
            raise RuntimeError("Redis 未初始化，请先调用 init()")
        return self._client

    # ──────────────────── 内部工具 ────────────────────

    def _key(self, key: str) -> str:
        """添加全局前缀"""
        return f"{self._prefix}{key}"

    def _encode(self, value: Any) -> Any:
        """编码值（非 str 转 JSON）"""
        if isinstance(value, (str, int, float, bytes)):
            return value
        return json.dumps(value, ensure_ascii=False)

    def _decode(self, value: Any, default: Any = None) -> Any:
        """解码值（尝试 JSON 解析）"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError, ValueError):
            return value

    # ──────────────────── 通用操作 ────────────────────

    async def set(self, key: str, value: Any, expire: int | None = None) -> Any:
        """设置键值，可选过期时间(秒)"""
        return await self.client.set(self._key(key), self._encode(value), ex=expire)

    async def setnx(self, key: str, value: Any, expire: int | None = None) -> bool:
        """仅当键不存在时设置"""
        ok = await self.client.setnx(self._key(key), self._encode(value))
        if ok and expire:
            await self.client.expire(self._key(key), expire)
        return ok

    async def get(self, key: str, default: Any = None) -> Any:
        """获取值，自动解码 JSON"""
        return self._decode(await self.client.get(self._key(key)), default)

    async def get_int(self, key: str, default: int = 0) -> int:
        """获取整型值"""
        val = await self.client.get(self._key(key))
        return int(val) if val is not None else default

    async def delete(self, *keys: str) -> int:
        """删除键，返回删除数量"""
        prefixed = [self._key(k) for k in keys]
        return await self.client.delete(*prefixed)

    async def exists(self, key: str) -> bool:
        """判断键是否存在"""
        return await self.client.exists(self._key(key)) > 0

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间(秒)"""
        return await self.client.expire(self._key(key), seconds)

    async def ttl(self, key: str) -> int:
        """获取剩余生存时间(秒)，-1 无过期，-2 不存在"""
        return await self.client.ttl(self._key(key))

    async def incr(self, key: str, amount: int = 1) -> int:
        """自增"""
        return await self.client.incr(self._key(key), amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """自减"""
        return await self.client.decr(self._key(key), amount)

    # ──────────────────── Set 操作 ────────────────────

    async def sadd(self, key: str, *members: Any) -> int:
        return await self.client.sadd(self._key(key), *[self._encode(m) for m in members])

    async def srem(self, key: str, *members: Any) -> int:
        return await self.client.srem(self._key(key), *[self._encode(m) for m in members])

    async def smembers(self, key: str) -> set[Any]:
        raw = await self.client.smembers(self._key(key))
        return {self._decode(m) for m in raw}

    async def sismember(self, key: str, member: Any) -> Any:
        return await self.client.sismember(self._key(key), self._encode(member))

    async def scard(self, key: str) -> int:
        return await self.client.scard(self._key(key))

    # ──────────────────── Hash 操作 ────────────────────

    async def hset(self, key: str, field: str, value: Any) -> int:
        return await self.client.hset(self._key(key), field, self._encode(value))

    async def hset_dict(self, key: str, mapping: dict[str, Any]) -> None:
        encoded = {k: self._encode(v) for k, v in mapping.items()}
        await self.client.hset(self._key(key), mapping=encoded)

    async def hget(self, key: str, field: str, default: Any = None) -> Any:
        return self._decode(await self.client.hget(self._key(key), field), default)

    async def hgetall(self, key: str) -> dict[str, Any]:
        raw = await self.client.hgetall(self._key(key))
        return {k: self._decode(v) for k, v in raw.items()}

    async def hdel(self, key: str, *fields: str) -> int:
        return await self.client.hdel(self._key(key), *fields)

    async def hlen(self, key: str) -> int:
        return await self.client.hlen(self._key(key))

    async def hexists(self, key: str, field: str) -> bool:
        return await self.client.hexists(self._key(key), field)

    # ──────────────────── List 操作 ────────────────────

    async def lpush(self, key: str, *values: Any) -> int:
        return await self.client.lpush(self._key(key), *[self._encode(v) for v in values])

    async def rpush(self, key: str, *values: Any) -> int:
        return await self.client.rpush(self._key(key), *[self._encode(v) for v in values])

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> list[Any]:
        raw = await self.client.lrange(self._key(key), start, end)
        return [self._decode(v) for v in raw]

    async def llen(self, key: str) -> int:
        return await self.client.llen(self._key(key))

    async def lrem(self, key: str, count: int, value: Any) -> int:
        return await self.client.lrem(self._key(key), count, self._encode(value))

    # ──────────────────── 缓存辅助 ────────────────────

    async def cache_get(self, key: str, expire: int | None = None) -> Any:
        """获取缓存，不存在时返回 None"""
        return await self.get(key)
    
    async def cache_set_no_expire(self, key: str, value: Any) -> bool:
        """设置缓存，默认 5 分钟过期"""
        return await self.set(key, value)

    async def cache_set(self, key: str, value: Any, expire: int = 300) -> bool:
        """设置缓存，默认 5 分钟过期"""
        return await self.set(key, value, expire=expire)

    async def cache_delete(self, key: str) -> int:
        """删除缓存"""
        return await self.delete(key)

    # ──────────────────── Sorted Set 操作 ────────────────────

    async def zadd(self, key: str, members: dict[str, float]) -> int:
        """向有序集合添加成员，score 为浮点数"""
        return await self.client.zadd(self._key(key), members)

    async def zrevrange(
        self, key: str, start: int = 0, end: int = -1, withscores: bool = False
    ) -> list[Any]:
        """按 score 降序返回范围内的成员"""
        return await self.client.zrevrange(
            self._key(key), start, end, withscores=withscores,
        )

    async def zcard(self, key: str) -> int:
        """获取有序集合的基数（成员数量）"""
        return await self.client.zcard(self._key(key))

    async def zrem(self, key: str, *members: str) -> int:
        """移除有序集合中的一个或多个成员"""
        return await self.client.zrem(self._key(key), *members)

    # ──────────────────── 分布式锁 ────────────────────

    async def lock(self, key: str, expire: int = 10) -> bool:
        """获取分布式锁（基于 setnx）"""
        return await self.setnx(f"lock:{key}", 1, expire)

    async def unlock(self, key: str) -> int:
        """释放分布式锁"""
        return await self.delete(f"lock:{key}")


# 全局 singleton 实例
redis_manager = RedisManager()
