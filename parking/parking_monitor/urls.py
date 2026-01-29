"""
URLs de l'application parking_monitor
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import traffic_views

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'status', views.ParkingStatusViewSet, basename='parking-status')
router.register(r'traffic/status', traffic_views.TrafficStatusViewSet, basename='traffic-status')

app_name = 'parking_monitor'

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),

    # Endpoints spécialisés parking
    path('upload-image/', views.upload_esp32_image, name='upload-image'),
    path('update/', views.update_parking_manual, name='update-manual'),
    
    # Endpoints trafic
    path('traffic/check/', traffic_views.check_traffic_now, name='check-traffic-now'),
]
