"""
Sérialiseurs DRF pour les APIs
"""

from rest_framework import serializers
from .models import ParkingStatus


class ParkingStatusSerializer(serializers.ModelSerializer):
    """Sérialise les données de statut du parking"""
    
    occupancy_percentage = serializers.SerializerMethodField()
    available_spaces = serializers.IntegerField(read_only=True)
    
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
            'image_path'
        ]
        read_only_fields = ['timestamp', 'available_spaces', 'occupancy_rate', 'status']
    
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
            'status'
        ]
        read_only_fields = fields
