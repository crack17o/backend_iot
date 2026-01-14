from django.db import models

class ParkingStatus(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('full', 'Full'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    occupied = models.IntegerField()
    available = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    occupancy_rate = models.FloatField(default=0.0)  # Pourcentage d'occupation

    def __str__(self):
        return f"{self.timestamp} - {self.status} ({self.occupied}/{self.occupied + self.available})"

    class Meta:
        ordering = ['-timestamp']