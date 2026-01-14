from django.contrib import admin
from .models import ParkingStatus

@admin.register(ParkingStatus)
class ParkingStatusAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'occupied', 'available', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('timestamp',)
    readonly_fields = ('timestamp',)