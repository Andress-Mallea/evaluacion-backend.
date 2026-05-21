from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional

# --- Esquemas existentes ---
class RestaurantListResponse(BaseModel):
    id: UUID
    name: str

# --- Nuevos Esquemas para las Lógicas de Negocio ---
class CapacityCheckResponse(BaseModel):
    table_type_id: UUID
    table_type_name: str
    max_capacity_tables: int
    occupied_tables: int
    available_tables: int
    is_available: bool

class ReservationDetailResponse(BaseModel):
    id: UUID
    restaurant_name: str
    table_type_name: str
    reservation_time: datetime
    status: str
    guests: List[str] = []