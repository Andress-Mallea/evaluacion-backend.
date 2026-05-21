from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from datetime import datetime
from schemas import CapacityCheckResponse, ReservationDetailResponse
from services import RestaurantService

# ... (Mantener las funciones de proveedores de dependencias get_repo, get_cache, get_restaurant_service) ...

# Endpoint - Lógica de Negocio 1 (Capacidad) [cite: 862]
@router.get("/tables/{table_type_id}/availability", response_model=CapacityCheckResponse)
async def get_capacity(
    table_type_id: str,
    time: datetime = Query(..., description="Formato ISO: 2026-05-22T20:00:00"),
    service: RestaurantService = Depends(get_restaurant_service)
):
    try:
        return await service.check_table_availability(table_type_id, time)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Endpoint - Lógica de Negocio 2 (Ventana de Tiempo + Timezone) 
@router.get("/reservations/upcoming", response_model=List[ReservationDetailResponse])
async def list_upcoming_reservations(
    window_hours: int = Query(24, ge=1),
    timezone: str = Query("UTC", description="Ejemplo: America/La_Paz, Europe/Madrid"),
    service: RestaurantService = Depends(get_restaurant_service)
):
    return await service.get_upcoming_reservations(window_hours, timezone)