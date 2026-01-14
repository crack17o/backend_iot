"""
Application Django pour la surveillance de parking IoT

Système intelligent de détection de voitures garées via ESP32-CAM
utilisant YOLOv10 et une API REST Django.

Endpoints:
  - GET /api/parking_monitor/status/ - Historique
  - GET /api/parking_monitor/status/latest/ - Dernier statut
  - GET /api/parking_monitor/status/stats/ - Statistiques
  - POST /api/parking_monitor/upload-image/ - Upload ESP32
  - POST /api/parking_monitor/update/ - Mise à jour manuelle
"""

default_app_config = 'parking_monitor.apps.ParkingMonitorConfig'
