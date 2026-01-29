"""
Modèles de données pour le système de parking
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.core.cache import cache


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
        default=20,  # Capacité fixée à 20 véhicules
        validators=[MinValueValidator(1)],
        help_text="Quota total de places"
    )
    available = models.IntegerField(
        default=20,
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
        """Calcule automatiquement les champs dérivés (authorise occupied > total_spaces en heures de pointe)"""
        # Ne pas plafonner occupied : en embouteillage le parking peut dépasser le seuil
        self.occupied = max(0, self.occupied)

        # Places disponibles : 0 si dépassement
        self.available = max(0, self.total_spaces - self.occupied)

        # Taux d'occupation (peut dépasser 100 % en cas de surcharge)
        self.occupancy_rate = (self.occupied / self.total_spaces * 100) if self.total_spaces > 0 else 0

        # Statut : complet dès que capacity atteinte ou dépassée
        self.status = 'full' if self.occupied >= self.total_spaces else 'available'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.get_status_display()} ({self.occupied}/{self.total_spaces})"

    def get_occupancy_percentage(self):
        """Retourne un pourcentage formaté"""
        return f"{self.occupancy_rate:.1f}%"


class TrafficStatus(models.Model):
    """
    Modèle pour enregistrer l'état du trafic sur le trajet fixe
    Les coordonnées sont définies dans constants.py
    """
    TRAFFIC_CHOICES = [
        ('fluide', 'Fluide'),
        ('modere', 'Modéré'),
        ('embouteillage', 'Embouteillage'),
        ('bloque', 'Bloqué'),
    ]
    
    DIRECTION_CHOICES = [
        ('aller', 'Aller'),
        ('retour', 'Retour'),
    ]
    
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        default='aller',
        db_index=True,
        help_text="Direction du trajet (aller ou retour)"
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Données du trafic
    duration_seconds = models.IntegerField(
        help_text="Durée du trajet en secondes (temps réel)"
    )
    duration_in_traffic_seconds = models.IntegerField(
        help_text="Durée du trajet avec trafic en secondes"
    )
    distance_meters = models.IntegerField(
        help_text="Distance en mètres"
    )
    
    # Statut calculé
    traffic_status = models.CharField(
        max_length=20,
        choices=TRAFFIC_CHOICES,
        db_index=True,
        help_text="Statut du trafic"
    )
    delay_seconds = models.IntegerField(
        default=0,
        help_text="Délai dû au trafic en secondes"
    )
    delay_percentage = models.FloatField(
        default=0.0,
        help_text="Pourcentage de retard dû au trafic"
    )
    
    # Données brutes de l'API
    raw_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Données brutes de l'API Google Maps"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['traffic_status']),
            models.Index(fields=['direction']),
        ]
        verbose_name = "Traffic Status"
        verbose_name_plural = "Traffic Status"
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement les champs dérivés"""
        # Calculer le délai
        self.delay_seconds = max(0, self.duration_in_traffic_seconds - self.duration_seconds)
        
        # Calculer le pourcentage de retard
        if self.duration_seconds > 0:
            self.delay_percentage = (self.delay_seconds / self.duration_seconds) * 100
        else:
            self.delay_percentage = 0
        
        # Déterminer le statut du trafic (embouteillage à partir de 110 % de retard)
        if self.delay_percentage >= 200:
            self.traffic_status = 'bloque'
        elif self.delay_percentage >= 110:
            self.traffic_status = 'embouteillage'
        elif self.delay_percentage >= 10:
            self.traffic_status = 'modere'
        else:
            self.traffic_status = 'fluide'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_direction_display()} - {self.get_traffic_status_display()} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration_minutes(self):
        """Retourne la durée en minutes"""
        return self.duration_seconds / 60
    
    @property
    def duration_in_traffic_minutes(self):
        """Retourne la durée avec trafic en minutes"""
        return self.duration_in_traffic_seconds / 60
    
    @property
    def delay_minutes(self):
        """Retourne le délai en minutes"""
        return self.delay_seconds / 60
    
    @property
    def distance_km(self):
        """Retourne la distance en kilomètres"""
        return self.distance_meters / 1000


class SystemSettings(models.Model):
    """
    Modèle singleton pour les paramètres système
    Un seul enregistrement doit exister
    """
    google_maps_enabled = models.BooleanField(
        default=True,
        help_text="Activer les requêtes vers l'API Google Maps"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètres système"
        verbose_name_plural = "Paramètres système"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'un seul enregistrement
        self.pk = 1
        super().save(*args, **kwargs)
        # Invalider le cache
        cache.delete('system_settings')
    
    def delete(self, *args, **kwargs):
        # Empêcher la suppression
        pass
    
    @classmethod
    def get_settings(cls):
        """Récupère les paramètres système (avec cache)"""
        settings = cache.get('system_settings')
        if settings is None:
            settings, _ = cls.objects.get_or_create(pk=1)
            cache.set('system_settings', settings, 300)  # Cache 5 minutes
        return settings
    
    def __str__(self):
        return f"Paramètres système (Google Maps: {'Activé' if self.google_maps_enabled else 'Désactivé'})"
