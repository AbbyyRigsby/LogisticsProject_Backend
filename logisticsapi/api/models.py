from django.db import models

# Create your models here.
class Path(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance_km = models.FloatField()

    def __str__(self):
        return f"{self.origin} to {self.destination} - {self.distance_km} km"