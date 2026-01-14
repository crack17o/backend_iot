"""
Modèles de données pour le système de parking
"""

from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime


class ParkingStatus(models.Model):
    """Modèle principal : enregistre l'état du parking"""
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('full', 'Complet'),
    ]
    
    # Données principales
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    occupied = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Nombre de places occupées"
    )
    total_spaces = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)],
        help_text="Quota total de places"
    )
    available = models.IntegerField(
        default=15,
        validators=[MinValueValidator(0)],
        help_text="Nombre de places disponibles (calculé)"
    )
    
    # Statut et métriques
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True,
        help_text="Statut du parking"
    )
    occupancy_rate = models.FloatField(
        default=0.0,
        help_text="Pourcentage d'occupation"
    )
    
    # Traçabilité
    image_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Chemin de l'image ESP32-CAM"
    )
    source = models.CharField(
        max_length=50,
        choices=[
            ('esp32', 'ESP32-CAM'),
            ('video', 'Vidéo temps réel'),
            ('api', 'API manuelle'),
        ],
        default='esp32',
        db_index=True
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['source']),
        ]
        verbose_name_plural = "Parking Status"
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement les champs dérivés"""
        # Vérifier que occupied <= total_spaces
        self.occupied = min(self.occupied, self.total_spaces)
        
        # Calculer les places disponibles
        self.available = self.total_spaces - self.occupied
        
        # Calculer le taux d'occupation
        self.occupancy_rate = (self.occupied / self.total_spaces * 100) if self.total_spaces > 0 else 0
        
        # Déterminer le statut
        self.status = 'full' if self.occupied >= self.total_spaces else 'available'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.get_status_display()} ({self.occupied}/{self.total_spaces})"
    
    def get_occupancy_percentage(self):
        """Retourne un pourcentage formaté"""
        return f"{self.occupancy_rate:.1f}%"