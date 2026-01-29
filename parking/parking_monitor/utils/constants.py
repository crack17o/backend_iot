"""
Constantes et configuration du système de parking
"""

# Configuration du parking
PARKING_CAPACITY = 20  # Quota de places (fixé à 20 véhicules)
PARKING_NAME = "Parking Intelligence - IoT"

# Paramètres YOLO
MODEL_PATH = "yolov10n.pt"
VEHICLE_CLASSES = [2, 5, 7]  # car, bus, truck (COCO dataset)
CONF_THRESHOLD = 0.25  # Confiance minimale
IOU_THRESHOLD = 0.45   # IoU threshold

# Paramètres de tracking (vidéo temps réel)
STATIONARY_DISTANCE = 80  # pixels - distance max avant considérer comme immobile
PARKING_TIME = 5  # secondes - temps avant compter comme stationnée
UPDATE_INTERVAL = 10  # secondes - fréquence d'envoi API

# Résolution
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Limites API
MAX_HISTORY_RECORDS = 100
UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB

# Clé API simple pour l'ESP32 (à personnaliser en production)
ESP32_API_KEY = "CHANGE_ME_ESP32_KEY"

# Google Maps API
GOOGLE_MAPS_API_KEY = "AIzaSyC7_fbskwFKcDOZsOcyup9X8wx_SDxU8jY"  # À configurer avec votre clé API Google Maps

# Coordonnées GPS fixes pour le trajet (aller/retour)
# Point de départ : Kinshasa, M77W+WMM
ROUTE_START_LATITUDE = -4.335271   # Latitude point de départ
ROUTE_START_LONGITUDE = 15.296477  # Longitude point de départ
# Point d'arrivée : Kinshasa, 6F7QM78W+9W
ROUTE_END_LATITUDE = -4.3340132    # Latitude point d'arrivée
ROUTE_END_LONGITUDE = 15.2973434   # Longitude point d'arrivée

# Messages
PARKING_FULL_MESSAGE = "Parking plein - aucune place disponible"
PARKING_AVAILABLE_MESSAGE = "Places disponibles"
API_KEY = "SifHte2SJdnfJ3iiV86kfZpuNr0xXuXOxr_-otNuCyQ;
