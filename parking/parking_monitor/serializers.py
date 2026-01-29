"""
Sérialiseurs DRF pour les APIs
"""

from rest_framework import serializers
from .models import ParkingStatus, TrafficStatus


class ParkingStatusSerializer(serializers.ModelSerializer):
    """Sérialise les données de statut du parking"""

    occupancy_percentage = serializers.SerializerMethodField()
    available_spaces = serializers.IntegerField(source='available', read_only=True)

    class Meta:
        model = ParkingStatus
        fields = [
            'id',
            'timestamp',
            'occupied',
            'available_spaces',
            'total_spaces',
            'occupancy_percentage',
            'occupancy_rate',
            'status',
            'image_path',
            'source',
        ]
        read_only_fields = [
            'timestamp',
            'available_spaces',
            'occupancy_rate',
            'status',
            'occupancy_percentage',
        ]

    def get_occupancy_percentage(self, obj):
        """Retourne le pourcentage d'occupation"""
        return f"{obj.occupancy_rate:.1f}%"


class ParkingStatusCreateSerializer(serializers.ModelSerializer):
    """Sérialise la création/mise à jour du statut"""

    class Meta:
        model = ParkingStatus
        fields = ['occupied', 'total_spaces']

    def validate_occupied(self, value):
        if value < 0:
            raise serializers.ValidationError("Le nombre de places occupées doit être >= 0")
        return value

    def validate_total_spaces(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le quota doit être > 0")
        return value


class ParkingHistorySerializer(serializers.ModelSerializer):
    """Sérialise l'historique du parking"""

    class Meta:
        model = ParkingStatus
        fields = [
            'timestamp',
            'occupied',
            'available',
            'occupancy_rate',
            'status',
            'source',
        ]
        read_only_fields = fields


class TrafficStatusSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'état du trafic"""
    
    duration_minutes = serializers.SerializerMethodField()
    duration_in_traffic_minutes = serializers.SerializerMethodField()
    delay_minutes = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    
    class Meta:
        model = TrafficStatus
        fields = [
            'id',
            'direction',
            'timestamp',
            'duration_seconds',
            'duration_minutes',
            'duration_in_traffic_seconds',
            'duration_in_traffic_minutes',
            'distance_meters',
            'distance_km',
            'traffic_status',
            'delay_seconds',
            'delay_minutes',
            'delay_percentage',
            'raw_data'
        ]
        read_only_fields = [
            'id',
            'timestamp',
            'traffic_status',
            'delay_seconds',
            'delay_percentage'
        ]
    
    def get_duration_minutes(self, obj):
        """Retourne la durée en minutes"""
        return round(obj.duration_seconds / 60, 1)
    
    def get_duration_in_traffic_minutes(self, obj):
        """Retourne la durée avec trafic en minutes"""
        return round(obj.duration_in_traffic_seconds / 60, 1)
    
    def get_delay_minutes(self, obj):
        """Retourne le délai en minutes"""
        return round(obj.delay_seconds / 60, 1)
    
    def get_distance_km(self, obj):
        """Retourne la distance en kilomètres"""
        return round(obj.distance_meters / 1000, 2)
