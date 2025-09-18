from django.contrib import admin
from .models import Place, Hotel

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'place', 'location', 'latitude', 'longitude')
    search_fields = ('name', 'place__name')
    list_filter = ('place',)
