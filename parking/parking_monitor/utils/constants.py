"""
Constantes et configuration du système de parking
"""

# Configuration du parking
PARKING_CAPACITY = 15  # Quota de places
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

# Messages
PARKING_FULL_MESSAGE = "Parking plein - aucune place disponible"
PARKING_AVAILABLE_MESSAGE = "Places disponibles"
