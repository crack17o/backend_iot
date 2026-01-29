"""
APIs REST pour le système de parking
- Endpoints pour upload d'images (ESP32-CAM)
- Endpoints pour consultation du statut
- Endpoints pour historique et statistiques
- Export de rapports (CSV/PDF)
"""

from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta, datetime
import uuid
import csv
import io

from .models import ParkingStatus, TrafficStatus
from .serializers import (
    ParkingStatusSerializer,
    ParkingStatusCreateSerializer,
    ParkingHistorySerializer,
    TrafficStatusSerializer
)
from .filters import ParkingStatusFilter
from .utils.car_detector import CarDetectorAPI
from .utils.constants import PARKING_CAPACITY, UPLOAD_MAX_SIZE, ESP32_API_KEY
from .utils.reports import generate_pdf_report
from .utils.google_maps import GoogleMapsTrafficChecker


# ============================================================================
# PAGINATION
# ============================================================================
class SmallPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================================
# API VIEWSETS
# ============================================================================
class ParkingStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter le statut du parking
    - Authentification requise pour tous les utilisateurs
    - Lecture seule pour tous les utilisateurs authentifiés
    
    GET /api/parking/status/ - Liste historique
    GET /api/parking/status/<id>/ - Détail d'une entrée
    GET /api/parking/status/latest/ - Statut courant
    GET /api/parking/status/stats/ - Statistiques
    GET /api/parking/status/export-csv/ - Export CSV
    GET /api/parking/status/export-pdf/ - Export PDF
    """
    queryset = ParkingStatus.objects.all()
    serializer_class = ParkingStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ParkingStatusFilter
    ordering_fields = ['timestamp', 'occupancy_rate', 'status']
    ordering = ['-timestamp']
    pagination_class = SmallPagination
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        GET /api/parking/status/latest/
        Retourne le dernier statut enregistré
        """
        try:
            latest = ParkingStatus.objects.latest('timestamp')
            serializer = self.get_serializer(latest)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ParkingStatus.DoesNotExist:
            return Response(
                {"error": "Aucune donnée disponible"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        GET /api/parking/status/stats/
        Statistiques du parking (dernières 24h)
        """
        try:
            # Données des 24 dernières heures
            last_24h = timezone.now() - timedelta(hours=24)
            records = ParkingStatus.objects.filter(timestamp__gte=last_24h)
            
            if not records.exists():
                return Response(
                    {"error": "Pas de données pour les dernières 24h"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculs
            avg_occupancy = sum(r.occupancy_rate for r in records) / records.count()
            max_occupied = max(r.occupied for r in records)
            full_count = records.filter(status='full').count()
            
            return Response({
                "period": "last_24h",
                "total_records": records.count(),
                "average_occupancy": f"{avg_occupancy:.1f}%",
                "peak_occupied": max_occupied,
                "times_full": full_count,
                "current_status": {
                    "occupied": records.latest('timestamp').occupied,
                    "available": records.latest('timestamp').available,
                    "status": records.latest('timestamp').status
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        GET /api/parking/status/export-csv/
        Exporte l'historique du parking en CSV
        
        Query params:
            - start_date: Date de début (YYYY-MM-DD)
            - end_date: Date de fin (YYYY-MM-DD)
        """
        try:
            # Filtrer par dates si fournies
            queryset = self.filter_queryset(self.get_queryset())
            
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            # Créer le CSV
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="parking_report_{datetime.now().strftime("%Y%m%d")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'Date/Heure',
                'Places occupées',
                'Places disponibles',
                'Capacité totale',
                'Taux d\'occupation (%)',
                'Statut',
                'Source'
            ])
            
            for record in queryset:
                writer.writerow([
                    record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    record.occupied,
                    record.available,
                    record.total_spaces,
                    f"{record.occupancy_rate:.1f}",
                    record.get_status_display(),
                    record.get_source_display()
                ])
            
            return response
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """
        GET /api/parking/status/export-pdf/
        Exporte un rapport PDF de l'historique du parking
        
        Query params:
            - start_date: Date de début (YYYY-MM-DD)
            - end_date: Date de fin (YYYY-MM-DD)
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            # Générer le PDF
            pdf_buffer = generate_pdf_report(queryset, start_date, end_date)
            
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="parking_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
            
            return response
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# API ENDPOINTS SPÉCIALISÉS
# ============================================================================
@api_view(['POST'])
def upload_esp32_image(request):
    """
    POST /api/parking/upload-image/
    Upload une image depuis ESP32-CAM et détecte les voitures
    
    Authentification:
    - Via token API (header: X-API-Token) pour ESP32
    - Via JWT pour utilisateurs authentifiés
    
    Form-data:
        - image: <fichier image>
        - device_id: <id du dispositif> (optionnel si token API)
    
    Response:
        {
            "success": true,
            "occupied": 5,
            "available": 15,
            "status": "available",
            "occupancy_rate": "25.0%",
            "timestamp": "2024-01-14T10:30:45Z"
        }
    """
    try:
        # Vérifier la clé API simple pour l'ESP32
        api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')
        if api_key != ESP32_API_KEY:
            return Response(
                {"error": "Clé API invalide"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Vérifier l'image
        if 'image' not in request.FILES:
            return Response(
                {"error": "Aucune image fournie"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']

        # Vérifier la taille
        if image_file.size > UPLOAD_MAX_SIZE:
            return Response(
                {"error": f"Fichier trop volumineux (max {UPLOAD_MAX_SIZE//1024//1024}MB)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lire les données
        image_data = image_file.read()
        
        # Initialiser le détecteur
        detector = CarDetectorAPI(parking_capacity=PARKING_CAPACITY)
        
        # Détecter les voitures
        result = detector.process_image(image_data)
        
        if not result['success']:
            return Response(
                {"error": result.get('error', 'Erreur de détection')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sauvegarder l'image
        file_name = f"esp32_{uuid.uuid4().hex[:8]}.jpg"
        file_path = f"uploads/esp32/{datetime.now().strftime('%Y/%m/%d')}/{file_name}"
        saved_path = default_storage.save(file_path, ContentFile(image_data))
        
        # Créer l'enregistrement
        parking_status = ParkingStatus.objects.create(
            occupied=result['count'],
            total_spaces=PARKING_CAPACITY,
            image_path=saved_path,
            source='esp32',
        )
        
        # Répondre
        serializer = ParkingStatusSerializer(parking_status)
        return Response({
            **serializer.data,
            "detected_count": result['count']
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def update_parking_manual(request):
    """
    POST /api/parking/update/
    Mise à jour manuelle du statut (Admin uniquement)
    
    Body JSON:
        {
            "occupied": 5,
            "total_spaces": 20
        }
    
    Response: Même format que ParkingStatus
    """
    try:
        serializer = ParkingStatusCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Créer l'enregistrement
            parking_status = ParkingStatus.objects.create(
                occupied=serializer.validated_data['occupied'],
                total_spaces=serializer.validated_data.get('total_spaces', PARKING_CAPACITY),
                source='esp32',
            )
            
            response_serializer = ParkingStatusSerializer(parking_status)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
