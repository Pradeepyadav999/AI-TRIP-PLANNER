from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('ES', 'Spanish'),
        ('FR', 'French'),
        ('DE', 'German'),
        ('ZH', 'Chinese'),
        ('JA', 'Japanese'),
        ('AR', 'Arabic'),
        ('HI', 'Hindi'),
    ]
    
    TRAVEL_PREFERENCES = [
        ('adventure', 'Adventure'),
        ('culture', 'Culture'),
        ('family', 'Family'),
        ('solo', 'Solo'),
        ('relaxation', 'Relaxation'),
        ('food', 'Food & Culinary'),
        ('eco', 'Eco-Tourism'),
        ('luxury', 'Luxury'),
    ]
    
    BUDGET_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    ACCOUNT_STATUS = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ]
    
    # Link to user model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic info
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Travel preferences
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='EN')
    travel_preferences = models.CharField(max_length=20, choices=TRAVEL_PREFERENCES, default='adventure')
    travel_history = models.TextField(blank=True)
    budget_range = models.CharField(max_length=10, choices=BUDGET_CHOICES, default='medium')
    
    # Location
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    
    # Profile
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUS, default='active')
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

class Feedback(models.Model):
    """Model for user feedback"""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved')
    ]
    
    ENTITY_TYPE_CHOICES = [
        ('destination', 'Destination'),
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('activity', 'Activity')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    subject = models.CharField(max_length=100)
    message = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_response = models.TextField(blank=True, null=True)
    response_date = models.DateTimeField(blank=True, null=True)
    
    # New fields
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES, default='destination')
    entity_id = models.IntegerField(blank=True, null=True)
    photos = models.ImageField(upload_to='feedback_photos/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Feedback from {self.user.username} - {self.subject}"
