import redis.asyncio as redis
import json
from src.conf.config import settings

class RedisCache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        if self.redis is None:  # 🔹 Запобігає повторному підключенню
            self.redis = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            )

    async def set(self, key: str, value: dict, expire: int = 3600):
        """
        Зберігає значення в Redis з вказаним ключем.
        """
        if self.redis:
            await self.redis.set(key, json.dumps(value), ex=expire)

    async def get(self, key: str):
        """
        Отримує значення з Redis за ключем.
        """
        if self.redis:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        return None

    async def delete(self, key: str):
        """
        Видаляє значення з Redis.
        """
        if self.redis:
            await self.redis.delete(key)

redis_cache = RedisCache()
