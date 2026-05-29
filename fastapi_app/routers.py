from fastapi import APIRouter, Depends, Query, Request, HTTPException
from typing import List, Optional
from datetime import datetime, date as date_type
from schemas import CapacityCheckResponse, ReservationDetailResponse
from services import RestaurantService
from repositories import PostgresRestaurantRepository
from core.cache import RedisCache
from datetime import date
from typing import Optional
from schemas import (
    CapacityCheckResponse, ReservationDetailResponse, 
    PaginatedRestaurantResponse, RestaurantDetailResponse, RestaurantListResponse
)
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
    try:
        return await service.check_table_availability(table_type_id, time)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/healthz")
async def frontend_healthz():
    return {"status": "ok"}

@router.get("/tables/types/")
async def get_frontend_table_types(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, capacity FROM content.table_type")
        
        return [
            {
                "id": str(row["id"]), 
                "name": row["name"], 
                "seats": row["capacity"]
            } 
            for row in rows
        ]

@router.get("/menu/")
async def get_frontend_menu(date: date_type = Query(...)):
    return [
        {
            "course": "Entradas",
            "name": "Bruschetta de la Casa",
            "price": 12.0,
            "description": "Pan de masa madre, tomates cherry, ajo y albahaca fresca.",
            "allergens": ["Gluten"]
        },
        {
            "course": "Plato Principal",
            "name": "Lomo en Salsa de Vino Tinto",
            "price": 45.0,
            "description": "Corte jugoso acompañado de puré rústico y espárragos.",
            "allergens": ["Lácteos"]
        }
    ]
@router.get("/restaurants/{restaurant_id}/details", response_model=RestaurantDetailResponse)
async def get_restaurant_details(
    restaurant_id: str,
    service: RestaurantService = Depends(get_restaurant_service)
):
    try:
        return await service.get_restaurant_detail(restaurant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/reservations/availability/")
async def get_frontend_availability(
    request: Request, 
    date: date_type = Query(...),
    party: int = Query(...),
    time: Optional[str] = Query("19:00"),
    table_type: Optional[str] = Query(None),
    tz: str = Query("UTC"),
    service: RestaurantService = Depends(get_restaurant_service)
):
    try:
        uuid_to_check = table_type
        
   
        if not uuid_to_check:
            async with request.app.state.db_pool.acquire() as conn:
                first_table = await conn.fetchrow("SELECT id FROM content.table_type LIMIT 1")
                if not first_table:
                    return [] 
                uuid_to_check = str(first_table["id"])
                
        target_time = datetime.combine(date, datetime.strptime(time, "%H:%M").time())
        result = await service.check_table_availability(uuid_to_check, target_time)
        
        return [
            {
                "time": time,
                "table_type": str(result["table_type_id"]),
                "table_type_name": result["table_type_name"],
                "table_type_desc": "Mesa recomendada para tu grupo.",
                "available_seats": result["available_tables"] * 4,
                "seats": result["max_capacity_tables"] * 4,
                "price_per_seat": 25.0
            }
        ]
    except ValueError:
        return []
    
    
@router.get("/restaurants/", response_model=PaginatedRestaurantResponse)
async def list_restaurants(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    service: RestaurantService = Depends(get_restaurant_service)
):
    """Lista todos los restaurantes con paginación."""
    return await service.get_paginated_restaurants(page, size)
#C2
@router.get("/restaurants/{restaurant_id}/menu")
async def get_menu(
    restaurant_id: str,
    date: date,
    exclude_allergens: Optional[str] = None,
    group_by: Optional[str] = None,
    service=Depends(get_restaurant_service)
):
    try:
        result = await service.get_restaurant_menu(
            restaurant_id=restaurant_id, 
            target_date=date, 
            exclude_allergens_str=exclude_allergens, 
            group_by=group_by
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#C3
@router.get("/restaurants/{restaurant_id}/turns")
async def get_turns(
    restaurant_id: str,
    date: date,
    tz: str = "America/La_Paz", # Usamos una zona horaria por defecto realista
    service=Depends(get_restaurant_service)
):
    try:
        result = await service.get_turns_availability(restaurant_id, date, tz)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#C4
@router.get("/restaurants/search/")
async def search_restaurants(
    query: str,
    cuisine: Optional[str] = None,
    price_range: Optional[str] = None,
    service = Depends(get_restaurant_service)
):
    try:
        result = await service.search_restaurants(query, cuisine, price_range)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#C5
@router.get("/restaurants/popular")
async def get_popular_restaurants(
    period: str = "7d",
    tz: str = "America/La_Paz",
    include: Optional[str] = None,
    service = Depends(get_restaurant_service)
):
    try:
        result = await service.get_popular_restaurants(period, tz, include)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

