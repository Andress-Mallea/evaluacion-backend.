from django.contrib import admin
from .models import Restaurant, TableType, MenuItem, Reservation, ReservationGuest
from .models import Turn
class TableTypeInline(admin.TabularInline):
    model = TableType
    extra = 1

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

class ReservationGuestInline(admin.TabularInline):
    model = ReservationGuest
    extra = 1

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified')
    search_fields = ('name',)
    inlines = [TableTypeInline, MenuItemInline]

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'table_type', 'reservation_time', 'status')
    list_filter = ('status', 'reservation_time', 'restaurant')
    search_fields = ('id', 'restaurant__name')
    inlines = [ReservationGuestInline]
@admin.register(TableType)
class TableTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'restaurant')
    search_fields = ('name',)
admin.site.register(MenuItem)
admin.site.register(ReservationGuest)
@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'start_time', 'end_time', 'is_closed')