"""
URLs pour les vues web (dashboard)
"""

from django.urls import path
from . import web_views

app_name = 'web'

urlpatterns = [
    path('', web_views.dashboard, name='dashboard'),
    path('live/', web_views.live_situation, name='live_situation'),
    path('parking/', web_views.parking_history, name='parking_history'),
    path('traffic/', web_views.traffic_history, name='traffic_history'),
    path('traffic/check/', web_views.check_traffic_now, name='check_traffic_now'),
    path('settings/', web_views.settings, name='settings'),
    path('toggle-google-maps/', web_views.toggle_google_maps, name='toggle_google_maps'),
]
