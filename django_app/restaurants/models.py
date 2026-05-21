import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

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