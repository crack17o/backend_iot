"""
Filtres pour les APIs (recherche, tri, etc)
"""

from django_filters import rest_framework as filters
from .models import ParkingStatus


class ParkingStatusFilter(filters.FilterSet):
    """Filtre pour les requêtes de statut du parking"""
    
    timestamp_after = filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='gte',
        label='Après (ISO datetime)'
    )
    timestamp_before = filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='lte',
        label='Avant (ISO datetime)'
    )
    status = filters.ChoiceFilter(
        choices=ParkingStatus.STATUS_CHOICES,
        label='Statut du parking'
    )
    is_full = filters.BooleanFilter(
        method='filter_is_full',
        label='Parking plein?'
    )
    
    class Meta:
        model = ParkingStatus
        fields = ['status']
    
    def filter_is_full(self, queryset, name, value):
        """Filtre par statut plein/disponible"""
        if value:
            return queryset.filter(status='full')
        else:
            return queryset.filter(status='available')
