import pytest
from datetime import datetime
from typing import List, Optional
from core.interfaces import RestaurantRepositoryInterface, CacheInterface
from services import RestaurantService

# 1. Mock de la Capa de Persistencia (Postgres)
class MockRestaurantRepository(RestaurantRepositoryInterface):
    def __init__(self):
        self.reservations = []
        self.table_details = {"id": "11111111-1111-1111-1111-111111111111", "name": "Mesa VIP"}

    async def get_all_restaurants(self, limit: int, offset: int) -> List[dict]:
        return [{"id": "11111111-1111-1111-1111-111111111111", "name": "Restaurante Test"}]

    async def get_restaurant_by_id(self, restaurant_id: str) -> Optional[dict]:
        return {"id": restaurant_id, "name": "Restaurante Test"}

    async def search_restaurants(self, query: str) -> List[dict]:
        return []

    async def get_table_type_details(self, table_type_id: str) -> Optional[dict]:
        if table_type_id == "invalid-uuid":
            return None
        return self.table_details

    async def count_occupied_tables(self, table_type_id: str, start: datetime, end: datetime) -> int:
        # Simulamos que hay 4 mesas ocupadas concurrentemente para el test matemático
        return 4

    async def get_reservations_in_window(self, start_time: datetime, end_time: datetime) -> List[dict]:
        return self.reservations

# 2. Mock de la Capa de Infraestructura de Caché (Redis)
class MockCache(CacheInterface):
    def __init__(self):
        self.store = {}
        self.is_connected = True

    async def get(self, key: str) -> Optional[str]:
        if not self.is_connected:
            raise Exception("Redis connection lost")
        return self.store.get(key)

    async def set(self, key: str, value: str, expire: int = 60) -> None:
        if not self.is_connected:
            raise Exception("Redis connection lost")
        self.store[key] = value

# 3. Fixtures de Pytest para inyectar en las pruebas
@pytest.fixture
def mock_repo():
    return MockRestaurantRepository()

@pytest.fixture
def mock_cache():
    return MockCache()

@pytest.fixture
def restaurant_service(mock_repo, mock_cache):
    return RestaurantService(mock_repo, mock_cache)