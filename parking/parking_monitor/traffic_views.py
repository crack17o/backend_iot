"""
Vues pour la gestion du trafic
Les coordonnées GPS sont fixes (définies dans constants.py)
"""

from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination

from .models import TrafficStatus
from .serializers import TrafficStatusSerializer
from .utils.google_maps import GoogleMapsTrafficChecker


# ============================================================================
# PAGINATION
# ============================================================================
class SmallPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================================
# TRAFIC
# ============================================================================
class TrafficStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter l'historique du trafic
    
    GET /api/traffic/status/ - Liste historique
    GET /api/traffic/status/<id>/ - Détail d'un enregistrement
    GET /api/traffic/status/latest/ - Dernier statut pour chaque direction
    GET /api/traffic/status/direction/<direction>/ - Historique d'une direction spécifique
    """
    queryset = TrafficStatus.objects.all()
    serializer_class = TrafficStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['timestamp', 'traffic_status', 'delay_percentage']
    ordering = ['-timestamp']
    pagination_class = SmallPagination
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        GET /api/traffic/status/latest/
        Retourne le dernier statut de trafic pour chaque direction (aller/retour)
        """
        try:
            latest_aller = TrafficStatus.objects.filter(direction='aller').order_by('-timestamp').first()
            latest_retour = TrafficStatus.objects.filter(direction='retour').order_by('-timestamp').first()
            
            result = {}
            if latest_aller:
                serializer = self.get_serializer(latest_aller)
                result['aller'] = serializer.data
            if latest_retour:
                serializer = self.get_serializer(latest_retour)
                result['retour'] = serializer.data
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='direction/(?P<direction>[^/.]+)')
    def direction_history(self, request, direction=None):
        """
        GET /api/traffic/status/direction/<direction>/
        Retourne l'historique du trafic pour une direction spécifique (aller ou retour)
        """
        if direction not in ['aller', 'retour']:
            return Response(
                {"error": "Direction doit être 'aller' ou 'retour'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            queryset = TrafficStatus.objects.filter(direction=direction).order_by('-timestamp')
            
            # Pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
def check_traffic_now(request):
    """
    POST /api/traffic/check/
    Vérifie le trafic en temps réel pour une direction (aller ou retour)
    et enregistre le résultat
    
    Body JSON:
    {
        "direction": "aller"  // ou "retour"
    }
    """
    direction = request.data.get('direction', 'aller')
    
    if direction not in ['aller', 'retour']:
        return Response(
            {"error": "Direction doit être 'aller' ou 'retour'"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Initialiser le vérificateur
        try:
            traffic_checker = GoogleMapsTrafficChecker()
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Vérifier le trafic
        result = traffic_checker.check_fixed_route(direction=direction)
        
        if not result.get('success'):
            return Response(
                {"error": result.get('error', 'Erreur lors de la vérification du trafic')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer l'enregistrement TrafficStatus
        traffic_status = TrafficStatus.objects.create(
            direction=direction,
            duration_seconds=result['duration_seconds'],
            duration_in_traffic_seconds=result['duration_in_traffic_seconds'],
            distance_meters=result['distance_meters'],
            raw_data=result.get('raw_data', {})
        )
        
        # Le statut et les délais sont calculés automatiquement dans save()
        serializer = TrafficStatusSerializer(traffic_status)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
