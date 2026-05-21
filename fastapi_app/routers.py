from fastapi import APIRouter, Depends, Query, Request, HTTPException
from typing import List
from datetime import datetime
from schemas import CapacityCheckResponse, ReservationDetailResponse
from services import RestaurantService
from repositories import PostgresRestaurantRepository
from core.cache import RedisCache

router = APIRouter()

def get_repo(request: Request) -> PostgresRestaurantRepository:
    return PostgresRestaurantRepository(request.app.state.db_pool)

def get_cache(request: Request) -> RedisCache:
    return RedisCache(request.app.state.redis_client)

def get_restaurant_service(
    repo: PostgresRestaurantRepository = Depends(get_repo),
    cache: RedisCache = Depends(get_cache)
) -> RestaurantService:
    return RestaurantService(repo, cache)

@router.get("/reservations/upcoming", response_model=List[ReservationDetailResponse])
async def get_upcoming_reservations(
    window_hours: int = Query(48, ge=1, le=168),
    timezone: str = Query("America/La_Paz"),
    service: RestaurantService = Depends(get_restaurant_service)
):
    return await service.get_upcoming_reservations(window_hours, timezone)

@router.get("/tables/{table_type_id}/availability", response_model=CapacityCheckResponse)
async def check_availability(
    table_type_id: str,
    time: datetime = Query(...),
    service: RestaurantService = Depends(get_restaurant_service)
):
    # ¡AQUÍ ESTÁ LA MAGIA! Atrapamos el error del servicio y devolvemos un 404
    try:
        return await service.check_table_availability(table_type_id, time)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))