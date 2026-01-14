from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import ParkingStatus

# Configuration
PARKING_CAPACITY = 20  # Capacité totale du parking

@api_view(['POST'])
def update_parking_status(request):
    """
    Endpoint pour mettre à jour le statut du parking
    POST /api/status/update/
    Body: {
        "occupied": 5,
        "capacity": 20
    }
    """
    try:
        occupied = request.data.get('occupied', 0)
        capacity = request.data.get('capacity', PARKING_CAPACITY)
        
        if occupied < 0 or capacity <= 0:
            return Response(
                {"error": "Invalid values. occupied >= 0 and capacity > 0"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        available = capacity - occupied
        occupancy_rate = (occupied / capacity * 100) if capacity > 0 else 0
        
        # Déterminer le statut
        status_type = 'full' if occupied >= capacity else 'available'
        
        # Créer l'enregistrement
        parking_status = ParkingStatus.objects.create(
            occupied=occupied,
            available=available,
            status=status_type,
            occupancy_rate=occupancy_rate
        )
        
        return Response({
            "success": True,
            "id": parking_status.id,
            "timestamp": parking_status.timestamp,
            "occupied": parking_status.occupied,
            "available": parking_status.available,
            "capacity": capacity,
            "occupancy_rate": f"{occupancy_rate:.1f}%",
            "status": parking_status.status
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def get_parking_status(request):
    """
    Récupère le statut actuel du parking
    GET /api/status/
    """
    try:
        # Récupérer le dernier statut enregistré
        latest = ParkingStatus.objects.latest('timestamp')
        
        return Response({
            "occupied": latest.occupied,
            "available": latest.available,
            "capacity": latest.occupied + latest.available,
            "occupancy_rate": f"{latest.occupancy_rate:.1f}%",
            "status": latest.status,
            "timestamp": latest.timestamp,
            "is_full": latest.status == 'full'
        }, status=status.HTTP_200_OK)
    
    except ParkingStatus.DoesNotExist:
        return Response(
            {"error": "No parking status data available"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def get_parking_history(request):
    """
    Récupère l'historique des statuts du parking (dernières 24h)
    GET /api/status/history/
    """
    try:
        history = ParkingStatus.objects.all()[:100]  # Derniers 100 enregistrements
        
        data = [
            {
                "timestamp": record.timestamp,
                "occupied": record.occupied,
                "available": record.available,
                "occupancy_rate": f"{record.occupancy_rate:.1f}%",
                "status": record.status
            }
            for record in history
        ]
        
        return Response({
            "count": len(data),
            "history": data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )