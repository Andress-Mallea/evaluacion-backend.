import zoneinfo
import json
from datetime import datetime, timedelta, date, time
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
            
        total_tables = table_info.get("capacity", 0) 
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
        cache_key = f"restaurant_detail:{restaurant_id}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        restaurant = await self.repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise ValueError("Restaurant not found")
        await self.cache.set(cache_key, json.dumps(restaurant), expire=300)
        return restauran
    async def get_restaurant_by_name(self, name: str) -> dict:
        restaurant = await self.repo.get_restaurant_by_name(name)
        return [dict(row) for row in restaurant]
    #C2
    async def get_restaurant_menu(self, restaurant_id: str, target_date: datetime.date, exclude_allergens_str: str, group_by: str) -> dict | list:
        # Convertimos el string "shellfish,peanuts" a una lista de Python ['shellfish', 'peanuts']
        allergens_list = []
        if exclude_allergens_str:
            allergens_list = [a.strip().lower() for a in exclude_allergens_str.split(",")]

        # Llamamos al repositorio
        raw_menu = await self.repo.get_menu_filtered(restaurant_id, target_date, allergens_list)

        # Si el usuario pidió agrupar por curso (group_by=course)
        if group_by == "course":
            grouped_menu = {}
            for item in raw_menu:
                course = item.get("course", "otros")
                if course not in grouped_menu:
                    grouped_menu[course] = []
                grouped_menu[course].append(item)
            return grouped_menu

        # Si no pidió agrupar, devolvemos la lista plana
        return raw_menu
    #C3
    async def get_turns_availability(self, restaurant_id: str, target_date: date, tz: str) -> list:
        turns = await self.repo.get_restaurant_turns(restaurant_id)
        total_capacity = await self.repo.get_restaurant_total_capacity(restaurant_id)

        result = []
        for turn in turns:
            # Si el turno fue marcado como cerrado en Django, devolvemos 0%
            if turn['is_closed']:
                result.append({
                    "name": turn['name'],
                    "capacity": total_capacity,
                    "confirmed_reservations": 0,
                    "occupancy_percentage": 0.0,
                    "is_closed": True
                })
                continue

            # Contamos los invitados de las reservas confirmadas en ese rango horario
            guests = await self.repo.get_turn_reservations_count(
                restaurant_id, target_date, tz, turn['start_time'], turn['end_time']
            )

            # Calculamos porcentaje
            occupancy = (guests / total_capacity * 100) if total_capacity > 0 else 0

            result.append({
                "name": turn['name'],
                "capacity": total_capacity,
                "confirmed_reservations": guests,
                "occupancy_percentage": round(occupancy, 2), # Redondeamos a 2 decimales
                "is_closed": False
            })

        return result
    #C4
    async def search_restaurants(self, query: str, cuisine: str = None, price_range: str = None) -> list:
        return await self.repo.search_restaurants(query, cuisine, price_range)
    #C5
    async def get_popular_restaurants(self, period: str, tz: str, include: str = None) -> list:
        # Convertir '7d' a un entero 7
        try:
            days = int(period.replace('d', '').replace('D', ''))
        except ValueError:
            days = 7 # Por defecto si escriben algo raro

        # Llamar a la consulta pesada
        trending = await self.repo.get_trending_restaurants(days, tz)

        # Si mandaron ?include=tables, enriquecemos la respuesta
        if include == 'tables':
            for restaurant in trending:
                popular_tables = await self.repo.get_most_booked_tables(restaurant['id'], days)
                restaurant['popular_tables'] = popular_tables

        return trending