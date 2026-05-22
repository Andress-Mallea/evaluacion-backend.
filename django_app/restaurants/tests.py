from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from .models import Restaurant, TableType, MenuItem, Reservation, ReservationGuest

class RestaurantDomainTests(TestCase):
    def setUp(self):
       
        self.restaurant = Restaurant.objects.create(name="La Trattoria Test")

    def test_restaurant_creation_and_str(self):
        """Test 1: Verifica que el restaurante se crea correctamente y su representación en texto es exacta."""
        self.assertEqual(self.restaurant.name, "La Trattoria Test")
        self.assertEqual(str(self.restaurant), "La Trattoria Test")

    def test_table_type_relationship(self):
        """Test 2: Verifica la relación 1:N entre Restaurante y Tipo de Mesa."""
        table = TableType.objects.create(
            restaurant=self.restaurant,
            name="Mesa VIP",
            capacity=4
        )
        self.assertEqual(table.restaurant.name, "La Trattoria Test")
        self.assertEqual(TableType.objects.filter(restaurant=self.restaurant).count(), 1)
        
    def test_menu_item_price_decimal(self):
        """Test 3: Verifica que el menú maneja correctamente los decimales financieros (precision/scale)."""
        item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name="Pasta Carbonara",
            price=Decimal('15.50')
        )
        self.assertEqual(item.price, Decimal('15.50'))
        self.assertEqual(item.restaurant, self.restaurant)

    def test_reservation_creation(self):
        """Test 4: Verifica la integridad referencial al crear una reserva con su mesa correspondiente."""
        table = TableType.objects.create(
            restaurant=self.restaurant,
            name="Mesa Normal",
            capacity=2
        )
        res = Reservation.objects.create(
            restaurant=self.restaurant,
            table_type=table,
            reservation_time=timezone.now(),
            status="PENDING"
        )
        self.assertEqual(res.status, "PENDING")
        self.assertEqual(res.table_type.capacity, 2)

    def test_cascade_delete_integrity(self):
        """Test 5: Verifica la eliminación en cascada. Si un restaurante quiebra/se borra, sus mesas deben desaparecer."""
        TableType.objects.create(
            restaurant=self.restaurant,
            name="Mesa Temporal",
            capacity=6
        )
      
        self.assertEqual(TableType.objects.count(), 1)
        
       
        self.restaurant.delete()
        
       
        self.assertEqual(TableType.objects.count(), 0)