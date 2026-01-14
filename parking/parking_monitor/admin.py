"""
Configuration Django Admin pour le parking_monitor
"""

from django.contrib import admin
from .models import ParkingStatus


@admin.register(ParkingStatus)
class ParkingStatusAdmin(admin.ModelAdmin):
    """Admin pour gérer les statuts du parking"""
    
    list_display = [
        'timestamp',
        'occupied',
        'available',
        'get_occupancy_percentage',
        'status',
        'source'
    ]
    
    list_filter = [
        'status',
        'source',
        'timestamp'
    ]
    
    search_fields = ['image_path']
    
    readonly_fields = [
        'timestamp',
        'occupied',
        'available',
        'occupancy_rate',
        'status',
        'get_occupancy_percentage'
    ]
    
    fieldsets = (
        ('Statut actuel', {
            'fields': (
                'timestamp',
                'occupied',
                'available',
                'total_spaces',
                'status'
            )
        }),
        ('Métriques', {
            'fields': (
                'occupancy_rate',
                'get_occupancy_percentage'
            )
        }),
        ('Traçabilité', {
            'fields': (
                'source',
                'image_path'
            )
        }),
    )
    
    def get_occupancy_percentage(self, obj):
        """Affiche le pourcentage d'occupation"""
        return obj.get_occupancy_percentage()
    get_occupancy_percentage.short_description = "Taux d'occupation"
    
    def has_add_permission(self, request):
        """Les statuts sont créés automatiquement"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Garder l'historique"""
        return False