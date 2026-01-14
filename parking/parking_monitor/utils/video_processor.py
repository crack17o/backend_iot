"""
Traitement vidéo temps réel pour détection et tracking de voitures garées

Utilise YOLOv10 + ByteTrack pour :
- Détecter les véhicules dans une vidéo
- Suivre les voitures stationnées
- Envoyer les données à l'API Django toutes les 10 secondes
"""

import cv2
import math
import time
import requests
import logging
from ultralytics import YOLO
from typing import Dict, Set, Tuple, Optional
from datetime import datetime

from .constants import (
    MODEL_PATH,
    VEHICLE_CLASSES,
    CONF_THRESHOLD,
    IOU_THRESHOLD,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    STATIONARY_DISTANCE,
    PARKING_TIME,
    UPDATE_INTERVAL,
    PARKING_CAPACITY
)

# Configuration du logging
logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Processeur vidéo pour détection et tracking des voitures
    
    Attributs:
        model_path (str): Chemin vers yolov10n.pt
        parking_capacity (int): Nombre de places de parking
        api_url (str): URL de l'API Django
    """
    
    def __init__(
        self,
        model_path: str = MODEL_PATH,
        parking_capacity: int = PARKING_CAPACITY,
        api_url: str = "http://localhost:8000/api/parking_monitor/update/"
    ):
        """
        Initialise le processeur vidéo
        
        Args:
            model_path: Chemin vers le modèle YOLO
            parking_capacity: Quota de places
            api_url: URL endpoint Django pour les mises à jour
        """
        self.model_path = model_path
        self.parking_capacity = parking_capacity
        self.api_url = api_url
        
        # Variables de tracking
        self.tracks: Dict[int, Dict] = {}  # id -> {center, parked_time, last_seen}
        self.parked_ids: Set[int] = set()
        
        # Temps
        self.current_time: float = 0.0
        self.last_log_time: float = 0.0
        self.last_api_update: float = 0.0
        
        # Charger le modèle
        self.model: Optional[YOLO] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Charge le modèle YOLOv10"""
        try:
            logger.info(f"Chargement du modèle YOLO depuis {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("✓ Modèle YOLO chargé avec succès")
        except Exception as e:
            logger.error(f"✗ Erreur lors du chargement du modèle : {str(e)}")
            raise
    
    def _send_status_to_api(self, occupied_count: int) -> bool:
        """
        Envoie le statut du parking à l'API Django
        
        Args:
            occupied_count: Nombre de places occupées
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            payload = {
                "occupied": occupied_count,
                "total_spaces": self.parking_capacity
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 201:
                data = response.json()
                occupancy = data.get('occupancy_percentage', 'N/A')
                status_msg = data.get('status', 'N/A')
                logger.info(
                    f"✓ API : Occupés {occupied_count}/{self.parking_capacity} "
                    f"({occupancy}) - {status_msg}"
                )
                return True
            else:
                logger.warning(f"✗ API erreur {response.status_code}: {response.text}")
                return False
        
        except requests.exceptions.ConnectionError:
            logger.error(f"✗ Impossible de se connecter à {self.api_url}")
            return False
        except Exception as e:
            logger.error(f"✗ Erreur API : {str(e)}")
            return False
    
    def _detect_cars(self, frame) -> Tuple[Dict[int, Tuple], bool]:
        """
        Détecte les voitures dans une frame
        
        Args:
            frame: Image à analyser
            
        Returns:
            Tuple: (dictionnaire des IDs détectés, succès)
        """
        if self.model is None:
            return {}, False
        
        try:
            # Exécuter YOLO + ByteTrack
            results = self.model.track(
                frame,
                tracker="bytetrack.yaml",
                conf=CONF_THRESHOLD,
                iou=IOU_THRESHOLD,
                classes=VEHICLE_CLASSES,
                persist=True,
                verbose=False
            )
            
            detected = {}
            
            if results and results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes
                ids = boxes.id.int().cpu().tolist()
                coords = boxes.xyxy.cpu().numpy()
                
                for i, track_id in enumerate(ids):
                    x1, y1, x2, y2 = coords[i]
                    center = ((x1 + x2) / 2, (y1 + y2) / 2)
                    detected[track_id] = center
            
            return detected, True
        
        except Exception as e:
            logger.error(f"Erreur détection YOLO : {str(e)}")
            return {}, False
    
    def _update_tracking(self, detected: Dict[int, Tuple], frame_time: float) -> None:
        """
        Met à jour l'état du tracking des voitures
        
        Args:
            detected: Dictionnaire des voitures détectées {id: (x, y)}
            frame_time: Temps écoulé depuis la dernière frame (secondes)
        """
        active_ids = set(detected.keys())
        
        for track_id, center in detected.items():
            # Nouvelle détection
            if track_id not in self.tracks:
                self.tracks[track_id] = {
                    "center": center,
                    "parked_time": 0,
                    "last_seen": self.current_time
                }
                continue
            
            # Voiture existante
            prev_center = self.tracks[track_id]["center"]
            distance = math.dist(center, prev_center)
            
            # Logique de stationnement
            if distance < STATIONARY_DISTANCE:
                self.tracks[track_id]["parked_time"] += frame_time
            else:
                self.tracks[track_id]["parked_time"] = max(
                    0,
                    self.tracks[track_id]["parked_time"] - frame_time
                )
            
            # Ajouter aux stationnées si critère atteint
            if self.tracks[track_id]["parked_time"] >= PARKING_TIME:
                self.parked_ids.add(track_id)
            
            # Mettre à jour position et temps
            self.tracks[track_id]["center"] = center
            self.tracks[track_id]["last_seen"] = self.current_time
        
        # Nettoyer les IDs perdus (pas vus depuis 2 secondes)
        self.tracks = {
            tid: data for tid, data in self.tracks.items()
            if self.current_time - data["last_seen"] < 2
        }
    
    def process_video(
        self,
        video_path: str,
        log_interval: float = 5.0,
        verbose: bool = True
    ) -> Dict:
        """
        Traite une vidéo complète et retourne les résultats
        
        Args:
            video_path: Chemin vers le fichier vidéo
            log_interval: Intervalle de log en secondes
            verbose: Afficher les logs console
            
        Returns:
            Dict: Résultats du traitement
        """
        logger.info(f"Traitement de la vidéo : {video_path}")
        
        # Ouvrir la vidéo
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"✗ Impossible d'ouvrir {video_path}")
            return {"success": False, "error": "Impossible d'ouvrir la vidéo"}
        
        # Paramètres vidéo
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_time = 1 / fps if fps > 0 else 0.033
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"FPS: {fps:.1f}, Frames: {total_frames}, Durée: {total_frames/fps:.1f}s")
        
        # Réinitialiser l'état
        self.tracks = {}
        self.parked_ids = set()
        self.current_time = 0.0
        self.last_log_time = 0.0
        self.last_api_update = 0.0
        
        frame_count = 0
        
        # Boucle principale
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Redimensionner
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            
            # Détecter
            detected, success = self._detect_cars(frame)
            if success:
                self._update_tracking(detected, frame_time)
            
            # Envoyer API toutes les 10 secondes
            if self.current_time - self.last_api_update >= UPDATE_INTERVAL:
                occupied = len(self.parked_ids)
                self._send_status_to_api(occupied)
                self.last_api_update = self.current_time
            
            # Log console
            if verbose and self.current_time - self.last_log_time >= log_interval:
                occupied = len(self.parked_ids)
                print(f"[{int(self.current_time):3d}s] Voitures stationnées : {occupied}/{self.parking_capacity}")
                self.last_log_time = self.current_time
            
            self.current_time += frame_time
            frame_count += 1
        
        # Cleanup
        cap.release()
        
        # Résumé final
        occupied_final = len(self.parked_ids)
        logger.info(f"✓ Analyse terminée")
        logger.info(f"Total voitures stationnées : {occupied_final}/{self.parking_capacity}")
        
        # Envoi final
        self._send_status_to_api(occupied_final)
        
        return {
            "success": True,
            "total_frames": frame_count,
            "duration": self.current_time,
            "occupied": occupied_final,
            "capacity": self.parking_capacity,
            "occupancy_rate": f"{(occupied_final/self.parking_capacity*100):.1f}%"
        }
    
    def analyze_single_frame(self, frame) -> Dict:
        """
        Analyse une seule frame (pour API)
        
        Args:
            frame: Image numpy
            
        Returns:
            Dict: Résultats de détection
        """
        if frame is None:
            return {"success": False, "error": "Frame vide"}
        
        try:
            # Redimensionner
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            
            # Détecter
            detected, success = self._detect_cars(frame)
            
            if not success:
                return {"success": False, "error": "Erreur détection"}
            
            return {
                "success": True,
                "count": len(detected),
                "vehicles": detected
            }
        
        except Exception as e:
            logger.error(f"Erreur analyse frame : {str(e)}")
            return {"success": False, "error": str(e)}


# ============================================================================
# FONCTIONS AUXILIAIRES
# ============================================================================

def process_video_file(video_path: str) -> Dict:
    """
    Fonction pratique pour traiter un fichier vidéo
    
    Args:
        video_path: Chemin vers la vidéo
        
    Returns:
        Dict: Résultats
    """
    processor = VideoProcessor()
    return processor.process_video(video_path, verbose=True)


def analyze_frame(frame, parking_capacity: int = PARKING_CAPACITY) -> Dict:
    """
    Fonction pratique pour analyser une seule frame
    
    Args:
        frame: Image numpy
        parking_capacity: Quota
        
    Returns:
        Dict: Résultats
    """
    processor = VideoProcessor(parking_capacity=parking_capacity)
    return processor.analyze_single_frame(frame)