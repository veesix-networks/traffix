from typing import Annotated
import json

from aioredis import from_url
from fastapi import Depends

from traffix.config import settings


class RedisDependency:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis_url = str(redis_url)
        self.redis = None

    async def connect(self):
        self.redis = await from_url(self.redis_url)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str, load_json: bool = True) -> str:
        data = await self.redis.get(key)
        if not data:
            return

        if load_json:
            return json.loads(data.decode("utf-8"))

        return data.decode("utf-8")

    async def set(self, key: str, value: str):
        await self.redis.set(key, value)


async def get_redis(redis_url: str = "redis://localhost"):
    client = RedisDependency(settings.REDIS)
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()


RedisDep = Annotated[RedisDependency, Depends(get_redis)]
