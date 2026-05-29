import random
from datetime import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from restaurants.models import Restaurant, TableType, MenuItem, Reservation, ReservationGuest, Turn

class Command(BaseCommand):
    help = 'Pobla de manera automatica la BD con los requerimientos C2, C3, C4 y C5'

    def handle(self, *args, **kwargs):
        # Si ya hay datos, le decimos al usuario cómo borrarlos
        def handle(self, *args, **kwargs):
            self.stdout.write('Limpiando base de datos antigua...')
            ReservationGuest.objects.all().delete()
            Reservation.objects.all().delete()
            MenuItem.objects.all().delete()
            Turn.objects.all().delete()
            TableType.objects.all().delete()
            Restaurant.objects.all().delete()

            self.stdout.write('Generando registros de prueba avanzados...')

        
        
        cuisines = ['italian', 'mexican', 'japanese', 'peruvian', 'bolivian']
        price_ranges = ['$', '$$', '$$$']
        courses = ['entrada', 'principal', 'postre', 'bebida']
        allergen_choices = ['dairy', 'gluten', 'shellfish', 'nuts', 'soy', 'fish', 'eggs']

        # 1. Crear Restaurantes (C4)
        # Reducimos un poco la cantidad a 30 para que no colapse con tanta data anidada
        restaurants = []
        for i in range(1, 31):
            restaurants.append(Restaurant(
                name=f"Restaurante Gourmet {i}",
                description=f"Una experiencia culinaria inolvidable en el restaurante {i}.",
                cuisine=random.choice(cuisines),
                price_range=random.choice(price_ranges)
            ))
        Restaurant.objects.bulk_create(restaurants)
        db_restaurants = Restaurant.objects.all()

        # 2. Tipos de Mesa, Menús (C2) y Turnos (C3)
        table_types_to_create = []
        menu_items_to_create = []
        turns_to_create = []
        
        for r in db_restaurants:
            # Mesas
            table_types_to_create.append(TableType(restaurant=r, name="Mesa Interior VIP", capacity=4))
            table_types_to_create.append(TableType(restaurant=r, name="Mesa Terraza", capacity=2))
            
            # Menú (5 platos aleatorios por restaurante)
            for _ in range(5):
                menu_items_to_create.append(MenuItem(
                    restaurant=r, 
                    name=f"Plato Especial {random.randint(1,1000)}", 
                    price=round(random.uniform(10.0, 50.0), 2),
                    course=random.choice(courses),
                    allergens=random.sample(allergen_choices, random.randint(0, 2)) # Asigna de 0 a 2 alérgenos
                ))
            
            # Turnos
            turns_to_create.append(Turn(restaurant=r, name="Almuerzo", start_time=time(12, 0), end_time=time(15, 0)))
            turns_to_create.append(Turn(restaurant=r, name="Cena", start_time=time(19, 0), end_time=time(23, 0)))

        TableType.objects.bulk_create(table_types_to_create)
        MenuItem.objects.bulk_create(menu_items_to_create)
        Turn.objects.bulk_create(turns_to_create)

        db_table_types = TableType.objects.all()
        
        # 3. Reservas (C5)
        reservations = []
        now = timezone.now()
        
        # Generar 1000 reservas históricas
        for _ in range(1000):
            tt = random.choice(db_table_types)
            # Fechas entre hace 20 días y hoy (Simula el "Trending")
            random_days = random.randint(-20, 0)
            random_hours = random.choice([13, 14, 19, 20, 21]) # Horas lógicas para comer
            
            res_time = now + timezone.timedelta(days=random_days)
            res_time = res_time.replace(hour=random_hours, minute=0, second=0)

            reservations.append(Reservation(
                restaurant=tt.restaurant,
                table_type=tt,
                reservation_time=res_time,
                status='confirmed'
            ))
        
        Reservation.objects.bulk_create(reservations)
        db_reservations = Reservation.objects.all()

        # 4. Invitados (C3)
        guests_to_create = []
        for res in db_reservations:
            # Ocupar la mesa con 1 hasta max_capacity personas
            num_guests = random.randint(1, res.table_type.capacity)
            for _ in range(num_guests):
                guests_to_create.append(ReservationGuest(
                    reservation=res,
                    full_name=f"Invitado Random {random.randint(1, 1000)}"
                ))
        
        ReservationGuest.objects.bulk_create(guests_to_create)

        self.stdout.write(self.style.SUCCESS('¡Seeding finalizado! Base de datos lista para pruebas C2, C3, C4 y C5.'))