import zoneinfo
from datetime import datetime, timedelta
from typing import List, Optional
from core.interfaces import RestaurantRepositoryInterface, CacheInterface

class RestaurantService:
    def __init__(self, repo: RestaurantRepositoryInterface, cache: CacheInterface):
        self.repo = repo
        self.cache = cache

    # ... (Mantener método get_restaurants) ...

    # LÓGICA 1: Control de capacidad bajo lectura concurrente 
    async def check_table_availability(self, table_type_id: str, target_time: datetime) -> dict:
        # Asumimos que una reserva bloquea la mesa por un intervalo de 2 horas
        start_window = target_time - timedelta(hours=1, minutes=59)
        end_window = target_time + timedelta(hours=1, minutes=59)
        
        # Al ejecutarse de forma asíncrona sobre asyncpg, soporta altas tasas de lectura concurrente
        occupied = await self.repo.count_occupied_tables(table_type_id, start_window, end_window)
        table_info = await self.repo.get_table_type_details(table_type_id)
        
        if not table_info:
            raise ValueError("El tipo de mesa especificado no existe.")
            
        # Supongamos que el restaurante cuenta con un número fijo de 10 mesas físicas de cada tipo 
        # (Esto se puede parametrizar o guardar en el modelo, lo fijamos en 10 para el ejemplo matemático)
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

    # LÓGICA 2: Filtrado por ventanas de tiempo con Timezones 
    async def get_upcoming_reservations(self, window_hours: int, tz_name: str) -> List[dict]:
        try:
            tz = zoneinfo.ZoneInfo(tz_name)
        except Exception:
            tz = zoneinfo.ZoneInfo("UTC") # Fallback seguro exigido por el brief [cite: 865]
            
        # Obtener el tiempo actual en la zona horaria del cliente [cite: 978]
        now_local = datetime.now(tz)
        end_local = now_local + timedelta(hours=window_hours)
        
        # Convertir a UTC para consultar la Base de Datos (Buena práctica de almacenamiento)
        start_utc = now_local.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)
        end_utc = end_local.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)
        
        return await self.repo.get_reservations_in_window(start_utc, end_utc)