from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='places/')

    def __str__(self):
        return self.name



class Hotel(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='hotels/')
    description = models.TextField(default="No description available.")  # Default text for description
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Ensure price is numeric

    def __str__(self):
        return self.name



class SavedTrip(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='saved_trips')
    destination = models.CharField(max_length=255)
    place_id = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    companions = models.CharField(max_length=50)
    activities = models.TextField()
    trip_html = models.TextField()
    origin_location = models.CharField(max_length=255, blank=True, null=True)
    transportation_mode = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s trip to {self.destination}"
    
    class Meta:
        ordering = ['-created_at']


