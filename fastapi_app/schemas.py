from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, UUID4
from decimal import Decimal

class RestaurantListResponse(BaseModel):
    id: UUID
    name: str


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
class MenuItemSchema(BaseModel):
    id: UUID4
    name: str
    price: Decimal

class TableTypeSchema(BaseModel):
    id: UUID4
    name: str
    capacity: int

class RestaurantListResponse(BaseModel):
    id: UUID4
    name: str
    created: datetime

class RestaurantDetailResponse(BaseModel):
    id: UUID4
    name: str
    created: datetime
    menus: List[MenuItemSchema] = []
    tables: List[TableTypeSchema] = []

class PaginatedRestaurantResponse(BaseModel):
    total: int
    page: int
    size: int
    results: List[RestaurantListResponse]