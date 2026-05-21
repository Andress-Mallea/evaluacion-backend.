import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from restaurants.models import Restaurant, TableType, MenuItem, Reservation, ReservationGuest

class Command(BaseCommand):
    help = 'Pobla de manera automatica la base de datos con los minimos del examen'

    def handle(self, *args, **kwargs):
        if Restaurant.objects.exists():
            self.stdout.write(self.style.WARNING('Datos existentes detectados. Omitiendo Seeding.'))
            return

        self.stdout.write('Generando registros de prueba masivos...')
        
  
        restaurants = [Restaurant(name=f"Restaurante Gourmet {i}") for i in range(1, 301)]
        Restaurant.objects.bulk_create(restaurants)
        db_restaurants = Restaurant.objects.all()

      
        table_types_to_create = []
        menu_items_to_create = []
        
        for r in db_restaurants:
            table_types_to_create.append(TableType(restaurant=r, name="Mesa Interior VIP", capacity=4))
            table_types_to_create.append(TableType(restaurant=r, name="Mesa Terraza", capacity=2))
            
            menu_items_to_create.append(MenuItem(restaurant=r, name="Plato de la Casa", price=25.50))
            menu_items_to_create.append(MenuItem(restaurant=r, name="Bebida Artesanal", price=8.00))

        TableType.objects.bulk_create(table_types_to_create)
        MenuItem.objects.bulk_create(menu_items_to_create)

       
        db_table_types = TableType.objects.all()
        reservations_to_create = []
        
       
        for _ in range(500):
            tt = random.choice(db_table_types)
            reservations_to_create.append(
                Reservation(
                    restaurant=tt.restaurant,
                    table_type=tt,
                    reservation_time=timezone.now() + timezone.timedelta(days=random.randint(1, 7))
                )
            )
        
        Reservation.objects.bulk_create(reservations_to_create)
        self.stdout.write(self.style.SUCCESS('Seeding finalizado correctamente.'))