import pytest
from datetime import datetime
import zoneinfo

@pytest.mark.asyncio
async def test_check_table_availability_success(restaurant_service):
    """Valida el cálculo correcto de mesas disponibles (10 totales - 4 ocupadas = 6)"""
    target_time = datetime(2026, 5, 22, 20, 0, 0)
    result = await restaurant_service.check_table_availability(
        table_type_id="11111111-1111-1111-1111-111111111111", 
        target_time=target_time
    )
    
    assert result["is_available"] is True
    assert result["occupied_tables"] == 4
    assert result["available_tables"] == 6
    assert result["max_capacity_tables"] == 10

@pytest.mark.asyncio
async def test_check_table_availability_not_found(restaurant_service):
    """Caso de Borde: Debe lanzar ValueError si el ID del tipo de mesa no existe"""
    with pytest.raises(ValueError, match="El tipo de mesa especificado no existe."):
        await restaurant_service.check_table_availability(
            table_type_id="invalid-uuid", 
            target_time=datetime.now()
        )

@pytest.mark.asyncio
async def test_get_upcoming_reservations_valid_timezone(restaurant_service, mock_repo):
    """Prueba el flujo feliz convirtiendo el huso horario de Bolivia a rangos UTC"""
    mock_repo.reservations = [
        {"id": "uuid-1", "restaurant_name": "Gourmet", "table_type_name": "VIP", "guests": ["Andres"]}
    ]
    
    records = await restaurant_service.get_upcoming_reservations(window_hours=48, tz_name="America/La_Paz")
    assert len(records) == 1
    assert records[0]["restaurant_name"] == "Gourmet"

@pytest.mark.asyncio
async def test_get_upcoming_reservations_invalid_timezone_fallback(restaurant_service):
    """Caso de Borde Exigido: Si el Timezone es inválido, debe aplicar Fallback a UTC sin colapsar"""

    records = await restaurant_service.get_upcoming_reservations(window_hours=24, tz_name="Zona/Inexistente_Bolivia")
    assert isinstance(records, list)