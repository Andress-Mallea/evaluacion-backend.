import json
import logging
from typing import Optional, Any

# Configuramos un logger para registrar las caídas sin romper la app
logger = logging.getLogger(__name__)

class RedisCache:
    # Aceptamos el cliente ya instanciado que nos pasa routers.py
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            # 🛡️ DEGRADACIÓN ELEGANTE
            logger.warning(f"Redis GET failed for {key}. Gracefully degrading to Postgres. Error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 300):
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            # 🛡️ DEGRADACIÓN ELEGANTE
            logger.warning(f"Redis SET failed for {key}. Proceeding without caching. Error: {e}")
            pass