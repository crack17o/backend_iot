import cv2
import numpy as np
from ultralytics import YOLO
import logging
import os

logger = logging.getLogger(__name__)

class CarDetectorAPI:
    """
    Version simplifiée pour API Django - traite une image unique
    Pas de tracking temporel, juste détection instantanée
    """
    
    def __init__(self, model_path="yolov10n.pt", parking_capacity=15):
        """
        Args:
            model_path: chemin vers yolov10n.pt
            parking_capacity: quota de places (15 dans ton cas)
        """
        self.parking_capacity = parking_capacity
        self.model_path = model_path
        self.model = None
        self.vehicle_classes = [2, 5, 7]  # car, bus, truck COCO IDs
        
        # Paramètres de détection (optimisés pour parking)
        self.conf_threshold = 0.25  # Plus sensible pour parking
        self.iou_threshold = 0.45
        
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle YOLO une fois"""
        try:
            logger.info(f"Chargement du modèle depuis {self.model_path}")
            
            # Vérifie si le fichier existe
            if not os.path.exists(self.model_path):
                logger.warning(f"Modèle non trouvé à {self.model_path}, téléchargement...")
                self.model = YOLO('yolov10n.pt')
                self.model.save(self.model_path)
            else:
                self.model = YOLO(self.model_path)
            
            # Configuration
            self.model.conf = self.conf_threshold
            self.model.iou = self.iou_threshold
            
            logger.info("Modèle YOLOv10 chargé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            raise
    
    def process_image(self, image_data):
        """
        Traite une image unique (bytes ou numpy array)
        Retourne le comptage et statut pour API
        
        Args:
            image_data: bytes de l'image ou numpy array
        
        Returns:
            dict avec count, is_full, etc.
        """
        try:
            # 1. Conversion des données
            if isinstance(image_data, bytes):
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif isinstance(image_data, np.ndarray):
                img = image_data
            else:
                raise ValueError("Format d'image non supporté")
            
            if img is None:
                raise ValueError("Impossible de décoder l'image")
            
            # 2. Redimensionnement optimal pour ESP32-CAM
            img_height, img_width = img.shape[:2]
            if img_width > 640 or img_height > 480:
                img = cv2.resize(img, (640, 480))
                logger.debug(f"Image redimensionnée: {img.shape}")
            
            # 3. Détection YOLO
            results = self.model(
                img,
                classes=self.vehicle_classes,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            # 4. Comptage
            count = 0
            detections_list = []
            
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None and len(boxes) > 0:
                    count = len(boxes)
                    
                    # Détails pour debug
                    for i, box in enumerate(boxes):
                        detections_list.append({
                            'id': i,
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].cpu().numpy().tolist(),
                            'class_id': int(box.cls[0])
                        })
            
            # 5. Calcul des métriques
            is_full = count >= self.parking_capacity
            available = max(0, self.parking_capacity - count)
            occupancy_rate = (count / self.parking_capacity * 100) if self.parking_capacity > 0 else 0
            
            logger.info(f"Détection: {count} véhicules, Full: {is_full}, Disponible: {available}")
            
            return {
                'success': True,
                'count': count,
                'is_full': is_full,
                'available': available,
                'total_spaces': self.parking_capacity,
                'occupancy_rate': round(occupancy_rate, 1),
                'detections_count': len(detections_list),
                'image_dimensions': f"{img_width}x{img_height}",
                'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
            }
            
        except Exception as e:
            logger.error(f"Erreur traitement image: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0,
                'is_full': False,
                'available': self.parking_capacity,
                'total_spaces': self.parking_capacity,
                'occupancy_rate': 0
            }

# Instance globale pour Django
car_detector = CarDetectorAPI(parking_capacity=15)