import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Restaurant(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(blank=True, null=True, help_text="Descripción del restaurante")
    cuisine = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: italian, mexican")
    price_range = models.CharField(max_length=10, blank=True, null=True, help_text="Ej: $, $$, $$$")
    class Meta:
        db_table = '"content"."restaurant"'
        verbose_name = _('Restaurant')
        verbose_name_plural = _('Restaurants')

    def __str__(self):
        return self.name

class TableType(UUIDMixin, TimeStampedMixin):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='table_types')
    name = models.CharField(_('name'), max_length=100)
    capacity = models.PositiveIntegerField(_('capacity'))

    class Meta:
        db_table = '"content"."table_type"'
        verbose_name = _('Table Type')
        verbose_name_plural = _('Table Types')

    def __str__(self):
        return f"{self.name} ({self.capacity} px) - {self.restaurant.name}"

class MenuItem(UUIDMixin, TimeStampedMixin):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(_('name'), max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField(null=True, blank=True, help_text="Fecha inicio de validez")
    valid_to = models.DateField(null=True, blank=True, help_text="Fecha fin de validez")
    course = models.CharField(max_length=50, default='principal', help_text="Ej: entrada, principal, postre")
    allergens = ArrayField(
        models.CharField(max_length=50), 
        blank=True, 
        default=list,
        help_text="Lista de alérgenos separados por coma en código"
    )
    class Meta:
        db_table = '"content"."menu_item"'
        verbose_name = _('Menu Item')
        verbose_name_plural = _('Menu Items')

    def __str__(self):
        return f"{self.name} (${self.price})"

class Reservation(UUIDMixin, TimeStampedMixin):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations')
    table_type = models.ForeignKey(TableType, on_delete=models.CASCADE, related_name='reservations')
    reservation_time = models.DateTimeField(_('reservation time'))
    status = models.CharField(_('status'), max_length=50, default='confirmed')

    class Meta:
        db_table = '"content"."reservation"'
        verbose_name = _('Reservation')
        verbose_name_plural = _('Reservations')

    def __str__(self):
        return f"Reserva {self.id} - {self.restaurant.name}"

class ReservationGuest(UUIDMixin, TimeStampedMixin):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='guests')
    full_name = models.CharField(_('full name'), max_length=255)

    class Meta:
        db_table = '"content"."reservation_guest"'
        verbose_name = _('Reservation Guest')
        verbose_name_plural = _('Reservation Guests')

    def __str__(self):
        return self.full_name
class Turn(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='turns')
    name = models.CharField(max_length=50, help_text="Ej: Almuerzo, Cena")
    start_time = models.TimeField(help_text="Hora de inicio (Ej: 12:00)")
    end_time = models.TimeField(help_text="Hora de fin (Ej: 15:00)")
    is_closed = models.BooleanField(default=False, help_text="¿El turno está cerrado ese día?")

    class Meta:
        db_table = '"content"."turn"'

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"    