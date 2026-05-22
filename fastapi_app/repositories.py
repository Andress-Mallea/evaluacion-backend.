import asyncpg
from datetime import datetime, timedelta
from typing import List, Optional
from core.interfaces import RestaurantRepositoryInterface

class PostgresRestaurantRepository(RestaurantRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    async def get_table_type_details(self, table_type_id: str) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            query = 'SELECT id, name, capacity, restaurant_id FROM content.table_type WHERE id = $1'
            row = await conn.fetchrow(query, table_type_id)
            return dict(row) if row else None

    async def count_occupied_tables(self, table_type_id: str, time_window_start: datetime, time_window_end: datetime) -> int:
        async with self.pool.acquire() as conn:
            query = """
                SELECT COUNT(*) FROM content.reservation 
                WHERE table_type_id = $1 
                  AND status = 'confirmed'
                  AND reservation_time >= $2 
                  AND reservation_time < $3
            """
            count = await conn.fetchval(query, table_type_id, time_window_start, time_window_end)
            return count if count else 0

    async def get_reservations_in_window(self, start_time: datetime, end_time: datetime) -> List[dict]:
        async with self.pool.acquire() as conn:
            query = """
                SELECT 
                    r.id, r.reservation_time, r.status,
                    res.name as restaurant_name,
                    tt.name as table_type_name,
                    COALESCE(array_agg(g.full_name) FILTER (WHERE g.full_name IS NOT NULL), '{}') as guests
                FROM content.reservation r
                JOIN content.restaurant res ON r.restaurant_id = res.id
                JOIN content.table_type tt ON r.table_type_id = tt.id
                LEFT JOIN content.reservation_guest g ON g.reservation_id = r.id
                WHERE r.reservation_time >= $1 AND r.reservation_time <= $2
                GROUP BY r.id, res.name, tt.name
                ORDER BY r.reservation_time ASC
            """
            rows = await conn.fetch(query, start_time, end_time)
            return [dict(row) for row in rows]
    async def get_restaurants(self, limit: int, offset: int) -> list:
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT id, name, created FROM content.restaurant ORDER BY created DESC LIMIT $1 OFFSET $2",
                limit, offset
            )

    async def count_restaurants(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM content.restaurant")

    async def get_restaurant_by_id(self, restaurant_id: str) -> dict:
        async with self.pool.acquire() as conn:
            restaurant = await conn.fetchrow(
                "SELECT id, name, created FROM content.restaurant WHERE id = $1", 
                restaurant_id
            )
            if not restaurant:
                return None
            
            menus = await conn.fetch(
                "SELECT id, name, price FROM content.menu_item WHERE restaurant_id = $1", 
                restaurant_id
            )
            
            tables = await conn.fetch(
                "SELECT id, name, capacity FROM content.table_type WHERE restaurant_id = $1", 
                restaurant_id
            )
            
            return {
                "id": restaurant["id"],
                "name": restaurant["name"],
                "created": restaurant["created"],
                "menus": [dict(m) for m in menus],
                "tables": [dict(t) for t in tables]
            }

    async def search_restaurants(self, query: str) -> list:
        async with self.pool.acquire() as conn:
            # ILIKE hace la búsqueda insensible a mayúsculas/minúsculas
            return await conn.fetch(
                "SELECT id, name, created FROM content.restaurant WHERE name ILIKE $1 ORDER BY name LIMIT 50",
                f"%{query}%"
            )