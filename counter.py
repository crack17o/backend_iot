from ultralytics import YOLO
import cv2
import sys
import time
import math
import requests
import json

# =========================
# CONFIGURATION
# =========================
MODEL_PATH = "yolov10n.pt"

VEHICLE_CLASS = 2            # Classe COCO : car
CONF_THRESHOLD = 0.4
IOU_THRESHOLD = 0.5

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

STATIONARY_DISTANCE = 80     # pixels (plus réaliste)
PARKING_TIME = 5             # secondes (test)

PARKING_CAPACITY = 20        # Capacité du parking
PARKING_API_URL = "http://localhost:8000/api/status/update/"
UPDATE_INTERVAL = 10         # Envoyer les données toutes les 10s

# =========================
# ARGUMENTS
# =========================
if len(sys.argv) < 2:
    print("Usage: python counter.py <video_file>")
    sys.exit(1)

VIDEO_PATH = sys.argv[1]

# =========================
# CHARGEMENT DU MODÈLE
# =========================
print("Chargement du modèle YOLO...")
model = YOLO(MODEL_PATH)

# =========================
# OUVERTURE VIDÉO
# =========================
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Erreur: impossible d'ouvrir {VIDEO_PATH}")
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_time = 1 / fps if fps > 0 else 0.033

# =========================
# VARIABLES DE TRACKING
# =========================
tracks = {}       # id -> {center, parked_time, last_seen}
parked_ids = set()

current_time = 0
last_log_time = 0
last_api_update = 0

print("Analyse de la vidéo en cours...")
print(f"Envoi des données à {PARKING_API_URL} toutes les {UPDATE_INTERVAL}s\n")

# =========================
# FONCTION D'ENVOI API
# =========================
def send_parking_status(occupied_count):
    """Envoie le statut du parking à l'API"""
    try:
        payload = {
            "occupied": occupied_count,
            "capacity": PARKING_CAPACITY
        }
        
        response = requests.post(
            PARKING_API_URL,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            occupancy = data.get('occupancy_rate', 'N/A')
            status_msg = data.get('status', 'N/A')
            print(f"[API] ✓ Mise à jour envoyée - Occupés: {occupied_count}/{PARKING_CAPACITY} ({occupancy}) - Statut: {status_msg}")
            return True
        else:
            print(f"[API] ✗ Erreur {response.status_code}: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"[API] ✗ Impossible de se connecter à {PARKING_API_URL}")
        return False
    except Exception as e:
        print(f"[API] ✗ Erreur: {str(e)}")
        return False

# =========================
# BOUCLE PRINCIPALE
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # -------------------------
    # YOLO + BYTE TRACK
    # -------------------------
    results = model.track(
        frame,
        tracker="bytetrack.yaml",
        conf=CONF_THRESHOLD,
        iou=IOU_THRESHOLD,
        classes=[VEHICLE_CLASS],
        persist=True,
        verbose=False
    )

    active_ids = set()

    if results and results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes
        ids = boxes.id.int().cpu().tolist()
        coords = boxes.xyxy.cpu().numpy()

        for i, track_id in enumerate(ids):
            active_ids.add(track_id)

            x1, y1, x2, y2 = coords[i]
            center = ((x1 + x2) / 2, (y1 + y2) / 2)

            if track_id not in tracks:
                tracks[track_id] = {
                    "center": center,
                    "parked_time": 0,
                    "last_seen": current_time
                }
                continue

            prev_center = tracks[track_id]["center"]
            distance = math.dist(center, prev_center)

            # -------- LOGIQUE ROBUSTE --------
            if distance < STATIONARY_DISTANCE:
                tracks[track_id]["parked_time"] += frame_time
            else:
                tracks[track_id]["parked_time"] = max(
                    0,
                    tracks[track_id]["parked_time"] - frame_time
                )

            if tracks[track_id]["parked_time"] >= PARKING_TIME:
                parked_ids.add(track_id)

            tracks[track_id]["center"] = center
            tracks[track_id]["last_seen"] = current_time

    # -------------------------
    # NETTOYAGE DES IDS PERDUS
    # -------------------------
    tracks = {
        tid: data for tid, data in tracks.items()
        if current_time - data["last_seen"] < 2
    }

    # -------------------------
    # ENVOI API TOUTES LES 10 SECONDES
    # -------------------------
    if current_time - last_api_update >= UPDATE_INTERVAL:
        occupied_count = len(parked_ids)
        send_parking_status(occupied_count)
        last_api_update = current_time

    # -------------------------
    # LOG CONSOLE
    # -------------------------
    if current_time - last_log_time >= 5:
        print(f"[{int(current_time)}s] Voitures stationnées: {len(parked_ids)}/{PARKING_CAPACITY}")
        last_log_time = current_time

    current_time += frame_time

# =========================
# FIN
# =========================
cap.release()

print("\nAnalyse terminée.")
print(f"Total voitures stationnées détectées : {len(parked_ids)}/{PARKING_CAPACITY}")
# Envoi final
send_parking_status(len(parked_ids))

