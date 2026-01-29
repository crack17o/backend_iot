"""
Configuration Django Admin pour le parking_monitor
"""

from django.contrib import admin
from .models import ParkingStatus, TrafficStatus, SystemSettings


@admin.register(ParkingStatus)
class ParkingStatusAdmin(admin.ModelAdmin):
    """Admin pour gérer les statuts du parking"""

    list_display = [
        'timestamp',
        'occupied',
        'available',
        'total_spaces',
        'get_occupancy_percentage',
        'status',
        'source',
    ]

    list_filter = [
        'status',
        'source',
        'timestamp',
    ]

    search_fields = [
        'image_path',
    ]

    readonly_fields = [
        'timestamp',
        'occupied',
        'available',
        'occupancy_rate',
        'status',
        'get_occupancy_percentage',
    ]

    fieldsets = (
        ('Statut actuel', {
            'fields': (
                'timestamp',
                'occupied',
                'available',
                'total_spaces',
                'status',
            )
        }),
        ('Métriques', {
            'fields': (
                'occupancy_rate',
                'get_occupancy_percentage',
            )
        }),
        ('Traçabilité', {
            'fields': (
                'source',
                'image_path',
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


@admin.register(TrafficStatus)
class TrafficStatusAdmin(admin.ModelAdmin):
    """Admin pour gérer les statuts de trafic"""
    
    list_display = [
        'direction',
        'timestamp',
        'traffic_status',
        'duration_minutes_display',
        'delay_minutes_display',
        'delay_percentage',
        'distance_km_display'
    ]
    
    list_filter = [
        'traffic_status',
        'direction',
        'timestamp'
    ]
    
    search_fields = [
        'direction'
    ]
    
    readonly_fields = [
        'timestamp',
        'traffic_status',
        'delay_seconds',
        'delay_percentage'
    ]
    
    def duration_minutes_display(self, obj):
        """Affiche la durée en minutes"""
        return f"{round(obj.duration_in_traffic_seconds / 60, 1)} min"
    duration_minutes_display.short_description = "Durée"
    
    def delay_minutes_display(self, obj):
        """Affiche le délai en minutes"""
        return f"+{round(obj.delay_seconds / 60, 1)} min"
    delay_minutes_display.short_description = "Délai"
    
    def distance_km_display(self, obj):
        """Affiche la distance en km"""
        return f"{round(obj.distance_meters / 1000, 2)} km"
    distance_km_display.short_description = "Distance"


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin pour les paramètres système"""
    
    def has_add_permission(self, request):
        # Un seul enregistrement autorisé
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression
        return False
    
    list_display = ['google_maps_enabled', 'updated_at']
    fields = ['google_maps_enabled']
    readonly_fields = ['updated_at']
    
    def changelist_view(self, request, extra_context=None):
        # Créer l'enregistrement s'il n'existe pas
        SystemSettings.get_settings()
        return super().changelist_view(request, extra_context)
