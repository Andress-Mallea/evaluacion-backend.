import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, Response
from routers import router
from config import settings

app = FastAPI(title="Public API Startup", docs_url="/api/openapi")

@app.on_event("startup")
async def startup():
    # Pool de Conexiones asíncronas Postgres
    app.state.db_pool = await asyncpg.create_pool(
        dsn=f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    # Cliente asíncrono Redis
    app.state.redis_client = redis.from_url(settings.REDIS_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()
    await app.state.redis_client.close()

@app.get("/healthz")
async def healthz(response: Response):
    try:
        async with app.state.db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception:
        response.status_code = 503
        return {"status": "unhealthy", "reason": "database connectivity issues"}

app.include_router(router)