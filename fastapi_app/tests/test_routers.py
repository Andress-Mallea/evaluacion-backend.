import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from routers import get_repo, get_cache
from tests.conftest import MockRestaurantRepository, MockCache

# 1. Aplicamos Inversión de Dependencias (SOLID):
app.dependency_overrides[get_repo] = lambda: MockRestaurantRepository()
app.dependency_overrides[get_cache] = lambda: MockCache()

@pytest.mark.asyncio
async def test_get_upcoming_reservations_endpoint():
    """Valida que la ruta de reservas responda un 200 OK y el JSON correcto"""
    # Nueva sintaxis requerida por httpx usando ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.get("/api/v1/reservations/upcoming?window_hours=48&timezone=America/La_Paz")
        
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "restaurant_name" in data[0]

@pytest.mark.asyncio
async def test_check_table_availability_endpoint():
    """Valida que la ruta de capacidad matemática devuelva la estructura esperada"""
    uuid_prueba = "11111111-1111-1111-1111-111111111111"
    url = f"/api/v1/tables/{uuid_prueba}/availability?time=2026-05-22T20:00:00"
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.get(url)
        
    assert response.status_code == 200
    data = response.json()
    assert data["is_available"] is True
    assert data["available_tables"] == 6

@pytest.mark.asyncio
async def test_check_table_availability_not_found_endpoint():
    """Valida que un UUID inválido en la ruta devuelva un código HTTP de error"""
    url = "/api/v1/tables/invalid-uuid/availability?time=2026-05-22T20:00:00"
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.get(url)
        
    assert response.status_code != 200