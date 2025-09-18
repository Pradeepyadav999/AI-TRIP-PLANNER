from django.urls import path
from .views import home, place_details, hotels_near_place,hotel_details,Trip, generate_ai_trip, payment_success, about, contact, weather, transportation_near_place
from django.views.generic import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', home, name='home'),
    path('trip/', Trip, name='trip'),
    path('place/<int:place_id>/', place_details, name='place_details'),
    path('place/<int:place_id>/hotels/', hotels_near_place, name='hotels_near_place'),
    path('place/<int:place_id>/transportation/', transportation_near_place, name='transportation_near_place'),
    path('hotel/<int:hotel_id>/', hotel_details, name='hotel_details'),
    path('hotel/<int:hotel_id>/payment-success/', payment_success, name='payment_success'),
    path('generate-ai-trip/', generate_ai_trip, name='generate_ai_trip'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    # Service worker path
    path('serviceworker.js', RedirectView.as_view(url=staticfiles_storage.url('serviceworker.js')), name='serviceworker'),
    path('weather/', weather, name='weather'),
]
