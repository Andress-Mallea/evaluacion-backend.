import zoneinfo
from datetime import datetime, timedelta
from typing import List, Optional
from core.interfaces import RestaurantRepositoryInterface, CacheInterface

class RestaurantService:
    def __init__(self, repo: RestaurantRepositoryInterface, cache: CacheInterface):
        self.repo = repo
        self.cache = cache
    async def check_table_availability(self, table_type_id: str, target_time: datetime) -> dict:
        start_window = target_time - timedelta(hours=1, minutes=59)
        end_window = target_time + timedelta(hours=1, minutes=59)
        
        occupied = await self.repo.count_occupied_tables(table_type_id, start_window, end_window)
        table_info = await self.repo.get_table_type_details(table_type_id)
        
        if not table_info:
            raise ValueError("El tipo de mesa especificado no existe.")
            
        total_tables = 10 
        available = total_tables - occupied
        
        return {
            "table_type_id": table_info["id"],
            "table_type_name": table_info["name"],
            "max_capacity_tables": total_tables,
            "occupied_tables": occupied,
            "available_tables": max(0, available),
            "is_available": available > 0
        }

    async def get_upcoming_reservations(self, window_hours: int, tz_name: str) -> List[dict]:
        try:
            tz = zoneinfo.ZoneInfo(tz_name)
        except Exception:
            tz = zoneinfo.ZoneInfo("UTC") 
            
        now_local = datetime.now(tz)
        end_local = now_local + timedelta(hours=window_hours)
       
        start_utc = now_local.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)
        end_utc = end_local.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)
        
        return await self.repo.get_reservations_in_window(start_utc, end_utc)
    async def get_paginated_restaurants(self, page: int, size: int) -> dict:
        offset = (page - 1) * size
        total = await self.repo.count_restaurants()
        rows = await self.repo.get_restaurants(limit=size, offset=offset)
        return {
            "total": total,
            "page": page,
            "size": size,
            "results": [dict(row) for row in rows]
        }

    async def get_restaurant_detail(self, restaurant_id: str) -> dict:
        restaurant = await self.repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise ValueError("Restaurant not found")
        return restaurant
    async def get_restaurant_by_name(self, name: str) -> dict:
        restaurant = await self.repo.get_restaurant_by_name(name)
        return [dict(row) for row in restaurant]
    async def search_restaurants(self, query: str) -> list:
        rows = await self.repo.search_restaurants(query)
        return [dict(row) for row in rows]