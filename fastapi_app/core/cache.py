from typing import Optional
import redis.asyncio as redis
from core.interfaces import CacheInterface

class RedisCache(CacheInterface):
    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client

    async def get(self, key: str) -> Optional[str]:
        # El método read-only asíncrono
        data = await self.client.get(key)
        return data.decode('utf-8') if data else None

    async def set(self, key: str, value: str, expire: int = 60) -> None:
        await self.client.set(key, value, ex=expire)