"""
Vues web pour le dashboard admin
Interface minimaliste et professionnelle avec Tailwind CSS
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Count

from .models import ParkingStatus, TrafficStatus, SystemSettings
from .utils.google_maps import GoogleMapsTrafficChecker
from .utils.constants import (
    PARKING_CAPACITY,
    ROUTE_START_LATITUDE,
    ROUTE_START_LONGITUDE,
    ROUTE_END_LATITUDE,
    ROUTE_END_LONGITUDE
)


def is_admin(user):
    """Vérifie si l'utilisateur est admin"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """
    Dashboard principal - Vue d'ensemble du système
    """
    # Dernier statut parking
    try:
        latest_parking = ParkingStatus.objects.latest('timestamp')
    except ParkingStatus.DoesNotExist:
        latest_parking = None
    
    # Statistiques parking (24h)
    last_24h = timezone.now() - timedelta(hours=24)
    parking_stats_24h = ParkingStatus.objects.filter(timestamp__gte=last_24h)
    
    parking_stats = {
        'total_records': parking_stats_24h.count(),
        'avg_occupancy': round(parking_stats_24h.aggregate(Avg('occupancy_rate'))['occupancy_rate__avg'] or 0, 1),
        'peak_occupied': parking_stats_24h.aggregate(Max('occupied'))['occupied__max'] or 0,
        'times_full': parking_stats_24h.filter(status='full').count(),
    }
    
    # Derniers statuts de trafic (aller et retour)
    latest_traffic_aller = TrafficStatus.objects.filter(direction='aller').order_by('-timestamp').first()
    latest_traffic_retour = TrafficStatus.objects.filter(direction='retour').order_by('-timestamp').first()
    
    # Statistiques trafic (24h)
    traffic_stats_24h = TrafficStatus.objects.filter(timestamp__gte=last_24h)
    traffic_stats = {
        'total_records': traffic_stats_24h.count(),
        'avg_delay_percentage': round(traffic_stats_24h.aggregate(Avg('delay_percentage'))['delay_percentage__avg'] or 0, 1),
        'embouteillages_count': traffic_stats_24h.filter(traffic_status__in=['embouteillage', 'bloque']).count(),
    }
    
    # Historique récent (5 derniers pour le parking)
    recent_parking = ParkingStatus.objects.all()[:5]
    recent_traffic = TrafficStatus.objects.all()[:10]
    
    context = {
        'latest_parking': latest_parking,
        'parking_stats': parking_stats,
        'parking_capacity': PARKING_CAPACITY,
        'latest_traffic_aller': latest_traffic_aller,
        'latest_traffic_retour': latest_traffic_retour,
        'traffic_stats': traffic_stats,
        'recent_parking': recent_parking,
        'recent_traffic': recent_traffic,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def parking_history(request):
    """
    Historique complet du parking avec filtres par date et heure
    """
    from datetime import datetime, time as dt_time
    
    # Filtrer par date et heure si fourni
    start_date = request.GET.get('start_date')
    start_time = request.GET.get('start_time', '00:00')
    end_date = request.GET.get('end_date')
    end_time = request.GET.get('end_time', '23:59')
    
    queryset = ParkingStatus.objects.all()
    
    # Construire les datetime de début et fin
    if start_date:
        try:
            start_datetime = datetime.combine(
                datetime.strptime(start_date, '%Y-%m-%d').date(),
                datetime.strptime(start_time, '%H:%M').time()
            )
            queryset = queryset.filter(timestamp__gte=start_datetime)
        except ValueError:
            pass  # Ignorer les dates invalides
    
    if end_date:
        try:
            end_datetime = datetime.combine(
                datetime.strptime(end_date, '%Y-%m-%d').date(),
                datetime.strptime(end_time, '%H:%M').time()
            )
            queryset = queryset.filter(timestamp__lte=end_datetime)
        except ValueError:
            pass  # Ignorer les dates invalides
    
    # Pagination avec 10 éléments par page
    from django.core.paginator import Paginator
    paginator = Paginator(queryset.order_by('-timestamp'), 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
    }
    
    return render(request, 'parking_history.html', context)


@login_required
@user_passes_test(is_admin)
def traffic_history(request):
    """
    Historique complet du trafic avec filtres par date, heure et direction
    """
    from datetime import datetime
    
    # Filtrer par direction, date et heure si fourni
    direction = request.GET.get('direction')
    start_date = request.GET.get('start_date')
    start_time = request.GET.get('start_time', '00:00')
    end_date = request.GET.get('end_date')
    end_time = request.GET.get('end_time', '23:59')
    
    queryset = TrafficStatus.objects.all()
    
    # Filtrer par direction
    if direction in ['aller', 'retour']:
        queryset = queryset.filter(direction=direction)
    
    # Construire les datetime de début et fin
    if start_date:
        try:
            start_datetime = datetime.combine(
                datetime.strptime(start_date, '%Y-%m-%d').date(),
                datetime.strptime(start_time, '%H:%M').time()
            )
            queryset = queryset.filter(timestamp__gte=start_datetime)
        except ValueError:
            pass  # Ignorer les dates invalides
    
    if end_date:
        try:
            end_datetime = datetime.combine(
                datetime.strptime(end_date, '%Y-%m-%d').date(),
                datetime.strptime(end_time, '%H:%M').time()
            )
            queryset = queryset.filter(timestamp__lte=end_datetime)
        except ValueError:
            pass  # Ignorer les dates invalides
    
    # Pagination avec 10 éléments par page
    from django.core.paginator import Paginator
    paginator = Paginator(queryset.order_by('-timestamp'), 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'selected_direction': direction,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
    }
    
    return render(request, 'traffic_history.html', context)


@login_required
@user_passes_test(is_admin)
def toggle_google_maps(request):
    """
    Active/désactive les requêtes vers l'API Google Maps
    """
    if request.method == 'POST':
        settings = SystemSettings.get_settings()
        settings.google_maps_enabled = not settings.google_maps_enabled
        settings.save()
        
        status = "activé" if settings.google_maps_enabled else "désactivé"
        from django.contrib import messages
        messages.success(request, f"API Google Maps {status}")
        
        # Si c'est une requête AJAX, retourner JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'enabled': settings.google_maps_enabled,
                'message': f"API Google Maps {status}"
            })
    
    return redirect('web:live_situation')


@login_required
@user_passes_test(is_admin)
def check_traffic_now(request):
    """
    Vérifie le trafic en temps réel et enregistre le résultat
    """
    if request.method == 'POST':
        direction = request.POST.get('direction', 'aller')
        
        # Vérifier si Google Maps est activé
        settings = SystemSettings.get_settings()
        if not settings.google_maps_enabled:
            error_msg = "API Google Maps désactivée par l'administrateur"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': error_msg,
                    'disabled': True
                }, status=400)
            from django.contrib import messages
            messages.error(request, error_msg)
            return redirect('web:live_situation')
        
        try:
            traffic_checker = GoogleMapsTrafficChecker()
            result = traffic_checker.check_fixed_route(direction=direction)
            
            if result.get('success'):
                # Créer l'enregistrement
                traffic_status = TrafficStatus.objects.create(
                    direction=direction,
                    duration_seconds=result['duration_seconds'],
                    duration_in_traffic_seconds=result['duration_in_traffic_seconds'],
                    distance_meters=result['distance_meters'],
                    raw_data=result.get('raw_data', {})
                )
                
                # Si c'est une requête AJAX, retourner JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    from .serializers import TrafficStatusSerializer
                    serializer = TrafficStatusSerializer(traffic_status)
                    return JsonResponse({
                        'success': True,
                        'message': f"Trafic vérifié avec succès pour la direction {direction}!",
                        'data': serializer.data
                    })
                
                # Sinon, rediriger avec un message
                from django.contrib import messages
                messages.success(request, f"Trafic vérifié avec succès pour la direction {direction}!")
                return redirect('web:live_situation')
            else:
                error_msg = result.get('error', 'Erreur inconnue')
                # Si c'est une requête AJAX, retourner JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'error': error_msg,
                        'disabled': result.get('disabled', False)
                    }, status=400)
                
                # Sinon, rediriger avec un message d'erreur
                from django.contrib import messages
                messages.error(request, f"Erreur: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            # Si c'est une requête AJAX, retourner JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
            
            # Sinon, rediriger avec un message d'erreur
            from django.contrib import messages
            messages.error(request, f"Erreur: {error_msg}")
    
    return redirect('web:dashboard')


@login_required
@user_passes_test(is_admin)
def settings(request):
    """
    Page de paramètres pour modifier les coordonnées GPS
    """
    # Lire les valeurs actuelles depuis constants.py
    from .utils import constants
    
    if request.method == 'POST':
        try:
            start_lat = float(request.POST.get('start_latitude'))
            start_lng = float(request.POST.get('start_longitude'))
            end_lat = float(request.POST.get('end_latitude'))
            end_lng = float(request.POST.get('end_longitude'))
            
            # Valider les coordonnées
            if not (-90 <= start_lat <= 90) or not (-90 <= end_lat <= 90):
                from django.contrib import messages
                messages.error(request, "Les latitudes doivent être entre -90 et 90")
                return render(request, 'settings.html', {
                    'start_latitude': request.POST.get('start_latitude'),
                    'start_longitude': request.POST.get('start_longitude'),
                    'end_latitude': request.POST.get('end_latitude'),
                    'end_longitude': request.POST.get('end_longitude'),
                })
            
            if not (-180 <= start_lng <= 180) or not (-180 <= end_lng <= 180):
                from django.contrib import messages
                messages.error(request, "Les longitudes doivent être entre -180 et 180")
                return render(request, 'settings.html', {
                    'start_latitude': request.POST.get('start_latitude'),
                    'start_longitude': request.POST.get('start_longitude'),
                    'end_latitude': request.POST.get('end_latitude'),
                    'end_longitude': request.POST.get('end_longitude'),
                })
            
            # Mettre à jour les constantes dans le fichier
            from pathlib import Path
            constants_file = Path(__file__).resolve().parent.parent / 'utils' / 'constants.py'
            
            # Lire le fichier
            with open(constants_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer les valeurs
            import re
            content = re.sub(
                r"ROUTE_START_LATITUDE\s*=\s*[\d.]+",
                f"ROUTE_START_LATITUDE = {start_lat}",
                content
            )
            content = re.sub(
                r"ROUTE_START_LONGITUDE\s*=\s*[\d.]+",
                f"ROUTE_START_LONGITUDE = {start_lng}",
                content
            )
            content = re.sub(
                r"ROUTE_END_LATITUDE\s*=\s*[\d.]+",
                f"ROUTE_END_LATITUDE = {end_lat}",
                content
            )
            content = re.sub(
                r"ROUTE_END_LONGITUDE\s*=\s*[\d.]+",
                f"ROUTE_END_LONGITUDE = {end_lng}",
                content
            )
            
            # Écrire le fichier
            with open(constants_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Recharger le module pour prendre en compte les nouvelles valeurs
            import importlib
            importlib.reload(constants)
            
            from django.contrib import messages
            messages.success(request, "Coordonnées GPS mises à jour avec succès!")
            
            # Rediriger vers la page de paramètres pour afficher les nouvelles valeurs
            return redirect('web:settings')
        
        except ValueError:
            from django.contrib import messages
            messages.error(request, "Veuillez entrer des valeurs numériques valides")
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    
    # Afficher les valeurs actuelles
    context = {
        'start_latitude': ROUTE_START_LATITUDE,
        'start_longitude': ROUTE_START_LONGITUDE,
        'end_latitude': ROUTE_END_LATITUDE,
        'end_longitude': ROUTE_END_LONGITUDE,
    }
    
    return render(request, 'settings.html', context)


@login_required
@user_passes_test(is_admin)
def live_situation(request):
    """
    Page de situation en temps réel - Affiche uniquement les données de moins d'1 minute
    """
    from datetime import timedelta
    
    # Seuil : 1 minute
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    
    # Dernier statut parking (moins d'1 minute)
    latest_parking = ParkingStatus.objects.filter(timestamp__gte=one_minute_ago).order_by('-timestamp').first()
    
    # Derniers statuts de trafic (moins d'1 minute)
    latest_traffic_aller = TrafficStatus.objects.filter(
        direction='aller',
        timestamp__gte=one_minute_ago
    ).order_by('-timestamp').first()
    
    latest_traffic_retour = TrafficStatus.objects.filter(
        direction='retour',
        timestamp__gte=one_minute_ago
    ).order_by('-timestamp').first()
    
    # Vérifier si les données sont à jour
    parking_is_fresh = latest_parking is not None
    traffic_aller_is_fresh = latest_traffic_aller is not None
    traffic_retour_is_fresh = latest_traffic_retour is not None
    
    # Si pas de données récentes, prendre les dernières disponibles (pour info)
    if not latest_parking:
        latest_parking = ParkingStatus.objects.order_by('-timestamp').first()
    
    if not latest_traffic_aller:
        latest_traffic_aller = TrafficStatus.objects.filter(direction='aller').order_by('-timestamp').first()
    
    if not latest_traffic_retour:
        latest_traffic_retour = TrafficStatus.objects.filter(direction='retour').order_by('-timestamp').first()
    
    # Coordonnées GPS pour la carte
    from .utils.constants import (
        ROUTE_START_LATITUDE,
        ROUTE_START_LONGITUDE,
        ROUTE_END_LATITUDE,
        ROUTE_END_LONGITUDE,
        GOOGLE_MAPS_API_KEY
    )
    
    # Récupérer les paramètres système
    settings = SystemSettings.get_settings()
    
    context = {
        'latest_parking': latest_parking,
        'parking_is_fresh': parking_is_fresh,
        'parking_capacity': PARKING_CAPACITY,
        'latest_traffic_aller': latest_traffic_aller,
        'traffic_aller_is_fresh': traffic_aller_is_fresh,
        'latest_traffic_retour': latest_traffic_retour,
        'traffic_retour_is_fresh': traffic_retour_is_fresh,
        'one_minute_ago': one_minute_ago,
        'start_latitude': ROUTE_START_LATITUDE,
        'start_longitude': ROUTE_START_LONGITUDE,
        'end_latitude': ROUTE_END_LATITUDE,
        'end_longitude': ROUTE_END_LONGITUDE,
        'google_maps_api_key': GOOGLE_MAPS_API_KEY if GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != "VOTRE_CLE_API_GOOGLE_MAPS" else None,
        'google_maps_enabled': settings.google_maps_enabled,
    }
    
    return render(request, 'live_situation.html', context)
