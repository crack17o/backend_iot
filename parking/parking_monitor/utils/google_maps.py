"""
Utilitaires pour interagir avec l'API Google Maps
- Directions API pour obtenir les informations de trafic
"""

import googlemaps
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

from ..utils.constants import (
    GOOGLE_MAPS_API_KEY,
    ROUTE_START_LATITUDE,
    ROUTE_START_LONGITUDE,
    ROUTE_END_LATITUDE,
    ROUTE_END_LONGITUDE
)
from ..models import SystemSettings

logger = logging.getLogger(__name__)


class GoogleMapsTrafficChecker:
    """
    Classe pour vérifier l'état du trafic via Google Maps API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le client Google Maps
        
        Args:
            api_key: Clé API Google Maps (si None, utilise celle des constantes)
        """
        self.api_key = api_key or GOOGLE_MAPS_API_KEY
        
        if not self.api_key or self.api_key == "VOTRE_CLE_API_GOOGLE_MAPS":
            raise ValueError(
                "Clé API Google Maps non configurée. "
                "Configurez GOOGLE_MAPS_API_KEY dans parking_monitor/utils/constants.py"
            )
        
        try:
            self.client = googlemaps.Client(key=self.api_key)
            logger.info("Client Google Maps initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur initialisation Google Maps: {e}")
            raise
    
    def check_traffic(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        departure_time: Optional[datetime] = None
    ) -> Dict:
        """
        Vérifie l'état du trafic entre deux points GPS
        
        Args:
            start_lat: Latitude du point de départ
            start_lng: Longitude du point de départ
            end_lat: Latitude du point d'arrivée
            end_lng: Longitude du point d'arrivée
            departure_time: Heure de départ (None = maintenant)
        
        Returns:
            dict avec les informations de trafic:
            {
                'success': bool,
                'duration_seconds': int,  # Temps sans trafic
                'duration_in_traffic_seconds': int,  # Temps avec trafic
                'distance_meters': int,
                'delay_seconds': int,
                'delay_percentage': float,
                'traffic_status': str,  # 'fluide', 'modere', 'embouteillage', 'bloque'
                'raw_data': dict
            }
        """
        try:
            # Vérifier si Google Maps est activé
            settings = SystemSettings.get_settings()
            if not settings.google_maps_enabled:
                logger.warning("Google Maps API désactivée par l'administrateur")
                return {
                    'success': False,
                    'error': 'API Google Maps désactivée par l\'administrateur',
                    'disabled': True
                }
            
            # Utiliser des tuples de coordonnées (lat, lng) - méthode la plus fiable
            # Les coordonnées négatives (-4.33...) indiquent clairement qu'on est en RDC (Kinshasa)
            origin = (start_lat, start_lng)
            destination = (end_lat, end_lng)
            
            # Si departure_time n'est pas fourni, utiliser maintenant
            if departure_time is None:
                departure_time = datetime.now()
            
            # Appel à l'API Directions
            # IMPORTANT: region="CD" (majuscules) = République Démocratique du Congo (RDC)
            # Ne pas confondre avec "CG" = République du Congo (Congo-Brazzaville)
            # Les coordonnées de Kinshasa (-4.33°, 15.29°) sont en RDC
            directions_result = self.client.directions(
                origin=origin,
                destination=destination,
                mode="driving",
                departure_time=departure_time,
                traffic_model="best_guess",  # Utilise les données de trafic en temps réel
                alternatives=False,
                region="CD"  # CD (majuscules) = République Démocratique du Congo (Kinshasa)
            )
            
            if not directions_result:
                return {
                    'success': False,
                    'error': 'Aucun itinéraire trouvé'
                }
            
            # Extraire les données de la première route
            route = directions_result[0]
            leg = route['legs'][0]
            
            # Durées
            duration_seconds = leg['duration']['value']  # Temps sans trafic
            duration_in_traffic_seconds = leg.get('duration_in_traffic', {}).get('value', duration_seconds)
            distance_meters = leg['distance']['value']
            
            # Calculer le délai
            delay_seconds = max(0, duration_in_traffic_seconds - duration_seconds)
            delay_percentage = (delay_seconds / duration_seconds * 100) if duration_seconds > 0 else 0
            
            # Déterminer le statut
            if delay_percentage >= 50:
                traffic_status = 'bloque'
            elif delay_percentage >= 30:
                traffic_status = 'embouteillage'
            elif delay_percentage >= 10:
                traffic_status = 'modere'
            else:
                traffic_status = 'fluide'
            
            return {
                'success': True,
                'duration_seconds': duration_seconds,
                'duration_in_traffic_seconds': duration_in_traffic_seconds,
                'distance_meters': distance_meters,
                'delay_seconds': delay_seconds,
                'delay_percentage': round(delay_percentage, 2),
                'traffic_status': traffic_status,
                'raw_data': {
                    'route': route,
                    'summary': route.get('summary', ''),
                    'warnings': route.get('warnings', [])
                }
            }
        
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Erreur API Google Maps: {e}")
            return {
                'success': False,
                'error': f"Erreur API Google Maps: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erreur vérification trafic: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_fixed_route(self, direction: str = 'aller') -> Dict:
        """
        Vérifie le trafic pour le trajet fixe défini dans constants.py
        
        Args:
            direction: 'aller' ou 'retour' (pour inverser départ/arrivée)
        
        Returns:
            dict avec les informations de trafic
        """
        if direction == 'retour':
            # Inverser départ et arrivée pour le retour
            return self.check_traffic(
                start_lat=ROUTE_END_LATITUDE,
                start_lng=ROUTE_END_LONGITUDE,
                end_lat=ROUTE_START_LATITUDE,
                end_lng=ROUTE_START_LONGITUDE
            )
        else:
            # Aller : départ -> arrivée
            return self.check_traffic(
                start_lat=ROUTE_START_LATITUDE,
                start_lng=ROUTE_START_LONGITUDE,
                end_lat=ROUTE_END_LATITUDE,
                end_lng=ROUTE_END_LONGITUDE
            )
