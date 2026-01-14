from django.urls import path
from .views import update_parking_status, get_parking_status, get_parking_history

urlpatterns = [
    path('status/', get_parking_status, name='get_parking_status'),
    path('status/update/', update_parking_status, name='update_parking_status'),
    path('status/history/', get_parking_history, name='parking_history'),
]