import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, Response
from routers import router

app = FastAPI(
    title="API de Restaurantes Examen", 
    docs_url="/api/openapi",        
    openapi_url="/api/openapi.json" 
)

@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(
        dsn="postgres://app_user:secure_password_here@db:5432/restaurant_db"
    )
    app.state.redis_client = redis.from_url("redis://redis:6379/0")

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
        return {"status": "unhealthy", "reason": "db error"}

app.include_router(router, prefix="/api/v1")