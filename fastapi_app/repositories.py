import asyncpg
from datetime import datetime, timedelta, date, time
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
    async def get_restaurant_by_name(self, name: str) -> list:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT id, name, created FROM content.restaurant WHERE name ILIKE = $1 ORDER BY name LIMIT 50", 
                f"%{name}%"
            )
    #C2
    async def get_menu_filtered(self, restaurant_id: str, target_date: datetime.date, exclude_allergens: list) -> list:
        # Consulta base: Filtramos por restaurante y que la fecha esté dentro del rango (o sea nula)
        query = """
            SELECT id, name, price, course, allergens
            FROM content.menu_item 
            WHERE restaurant_id = $1
            AND (valid_from IS NULL OR valid_from <= $2)
            AND (valid_to IS NULL OR valid_to >= $2)
        """
        params = [restaurant_id, target_date]

        # Si el usuario mandó alérgenos a excluir, agregamos el filtro de arrays de Postgres
        if exclude_allergens:
            query += " AND NOT (allergens && $3::varchar[])"
            params.append(exclude_allergens)

        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, *params)
            return [dict(r) for r in records]
    #C3
    async def get_restaurant_turns(self, restaurant_id: str) -> list:
        query = "SELECT id, name, start_time, end_time, is_closed FROM content.turn WHERE restaurant_id = $1 ORDER BY start_time"
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, restaurant_id)
            return [dict(r) for r in records]

    async def get_restaurant_total_capacity(self, restaurant_id: str) -> int:
        # Sumamos la capacidad de todos los tipos de mesa de este restaurante
        query = "SELECT COALESCE(SUM(capacity), 0) FROM content.table_type WHERE restaurant_id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, restaurant_id)

    async def get_turn_reservations_count(self, restaurant_id: str, target_date: date, tz: str, start_time: time, end_time: time) -> int:
        # Hacemos un JOIN con reservation_guest y usamos COUNT en lugar de SUM
        query = """
            SELECT COUNT(g.id) as total_guests
            FROM content.reservation r
            LEFT JOIN content.reservation_guest g ON r.id = g.reservation_id
            WHERE r.restaurant_id = $1
              AND r.status = 'confirmed'
              AND (r.reservation_time AT TIME ZONE $2)::date = $3
              AND (r.reservation_time AT TIME ZONE $2)::time >= $4
              AND (r.reservation_time AT TIME ZONE $2)::time <= $5
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(query, restaurant_id, tz, target_date, start_time, end_time)
            return result or 0
    #C4    
    async def search_restaurants(self, query_text: str, cuisine: str = None, price_range: str = None) -> list:
        # Consulta directa solo a la tabla de restaurantes
        query = """
        SELECT id, name, cuisine, price_range
        FROM content.restaurant
        WHERE 1=1
        """
        params = []
        param_idx = 1
        
        # 1. Full-Text Search EXCLUSIVO para el nombre del restaurante
        if query_text:
            query += f" AND to_tsvector('spanish', COALESCE(name, '')) @@ plainto_tsquery('spanish', ${param_idx})"
            params.append(query_text)
            param_idx += 1
            
        # 2. Filtro de Cocina (Cuisine)
        if cuisine:
            query += f" AND cuisine = ${param_idx}"
            params.append(cuisine)
            param_idx += 1
            
        # 3. Filtro de Precio (Price Range)
        if price_range:
            query += f" AND price_range = ${param_idx}"
            params.append(price_range)
            param_idx += 1

        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, *params)
            return [dict(r) for r in records]
    #C5
    async def get_trending_restaurants(self, days: int, tz: str) -> list:
        # VERSIÓN DE DIAGNÓSTICO: Quitamos el WHERE de crecimiento y usamos LEFT JOIN
        query = """
        WITH current_period AS (
            SELECT restaurant_id, COUNT(*) as current_count
            FROM content.reservation
            WHERE status = 'confirmed' 
              AND (reservation_time AT TIME ZONE $2) >= (CURRENT_TIMESTAMP AT TIME ZONE $2) - (INTERVAL '1 day' * $1::int)
            GROUP BY restaurant_id
        ),
        previous_period AS (
            SELECT restaurant_id, COUNT(*) as prev_count
            FROM content.reservation
            WHERE status = 'confirmed'
              AND (reservation_time AT TIME ZONE $2) >= (CURRENT_TIMESTAMP AT TIME ZONE $2) - (INTERVAL '1 day' * ($1::int * 2))
              AND (reservation_time AT TIME ZONE $2) < (CURRENT_TIMESTAMP AT TIME ZONE $2) - (INTERVAL '1 day' * $1::int)
            GROUP BY restaurant_id
        )
        SELECT 
            c.restaurant_id as id,
            r.name,
            c.current_count,
            COALESCE(p.prev_count, 0) as prev_count,
            CASE 
                WHEN COALESCE(p.prev_count, 0) = 0 THEN 0 
                ELSE ROUND(((c.current_count - p.prev_count) / p.prev_count::float) * 100) 
            END as growth_percentage
        FROM current_period c
        LEFT JOIN previous_period p ON c.restaurant_id = p.restaurant_id
        JOIN content.restaurant r ON c.restaurant_id = r.id
        ORDER BY c.current_count DESC
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, days, tz)
            return [dict(r) for r in records]
    async def get_most_booked_tables(self, restaurant_id: str, days: int) -> list:
        query = """
        SELECT tt.name, COUNT(r.id) as times_booked
        FROM content.reservation r
        JOIN content.table_type tt ON r.table_type_id = tt.id
        WHERE r.restaurant_id = $1 
          AND r.status = 'confirmed'
          AND r.reservation_time >= CURRENT_TIMESTAMP - (INTERVAL '1 day' * $2::int)
        GROUP BY tt.name
        ORDER BY times_booked DESC
        LIMIT 3
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, restaurant_id, days)
            return [dict(r) for r in records]
        # Busca cuáles fueron las mesas más reservadas en este periodo
        query = """
        SELECT tt.name, COUNT(r.id) as times_booked
        FROM content.reservation r
        JOIN content.table_type tt ON r.table_type_id = tt.id
        WHERE r.restaurant_id = $1 
          AND r.status = 'confirmed'
          AND r.reservation_time >= CURRENT_TIMESTAMP - ($2 || ' days')::interval
        GROUP BY tt.name
        ORDER BY times_booked DESC
        LIMIT 3
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, restaurant_id, days)
            return [dict(r) for r in records]