"""
Tests pour l'application parking_monitor
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from .models import ParkingStatus


class ParkingStatusModelTest(TestCase):
    """Tests du modèle ParkingStatus"""
    
    def setUp(self):
        """Préparation des tests"""
        self.parking = ParkingStatus.objects.create(
            occupied=5,
            total_spaces=15
        )
    
    def test_creation(self):
        """Test création d'un statut"""
        self.assertEqual(self.parking.occupied, 5)
        self.assertEqual(self.parking.total_spaces, 15)
        self.assertEqual(self.parking.available, 10)
    
    def test_occupancy_rate(self):
        """Test calcul du taux d'occupation"""
        expected = (5 / 15 * 100)
        self.assertAlmostEqual(self.parking.occupancy_rate, expected, places=1)
    
    def test_status_available(self):
        """Test statut disponible"""
        self.assertEqual(self.parking.status, 'available')
    
    def test_status_full(self):
        """Test statut complet"""
        full_parking = ParkingStatus.objects.create(
            occupied=15,
            total_spaces=15
        )
        self.assertEqual(full_parking.status, 'full')
    
    def test_occupied_exceeds_capacity(self):
        """Test que occupied ne peut pas dépasser capacity"""
        parking = ParkingStatus.objects.create(
            occupied=20,
            total_spaces=15
        )
        self.assertEqual(parking.occupied, 15)  # Limité à la capacité
    
    def test_string_representation(self):
        """Test la représentation string"""
        str_repr = str(self.parking)
        self.assertIn('available', str_repr)
        self.assertIn('5/15', str_repr)


class ParkingStatusAPITest(APITestCase):
    """Tests des APIs REST"""
    
    def setUp(self):
        """Préparation"""
        self.client = APIClient()
        
        # Créer quelques records
        self.parking1 = ParkingStatus.objects.create(
            occupied=5,
            total_spaces=15,
            source='esp32'
        )
        self.parking2 = ParkingStatus.objects.create(
            occupied=10,
            total_spaces=15,
            source='api'
        )
    
    def test_list_status(self):
        """Test GET /api/parking_monitor/status/"""
        response = self.client.get('/api/parking_monitor/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_latest(self):
        """Test GET /api/parking_monitor/status/latest/"""
        response = self.client.get('/api/parking_monitor/status/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['occupied'], 10)  # Plus récent
    
    def test_get_stats(self):
        """Test GET /api/parking_monitor/status/stats/"""
        response = self.client.get('/api/parking_monitor/status/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_occupancy', response.data)
        self.assertIn('peak_occupied', response.data)
    
    def test_update_parking_manual(self):
        """Test POST /api/parking_monitor/update/"""
        data = {
            'occupied': 8,
            'total_spaces': 15
        }
        response = self.client.post('/api/parking_monitor/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['occupied'], 8)
        self.assertEqual(response.data['status'], 'available')
    
    def test_update_invalid_data(self):
        """Test validation"""
        # occupied négatif
        data = {'occupied': -1, 'total_spaces': 15}
        response = self.client.post('/api/parking_monitor/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # total_spaces zéro
        data = {'occupied': 5, 'total_spaces': 0}
        response = self.client.post('/api/parking_monitor/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filter_by_status(self):
        """Test filtrage par statut"""
        # Créer un parking plein
        ParkingStatus.objects.create(occupied=15, total_spaces=15)
        
        response = self.client.get('/api/parking_monitor/status/?status=full')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_by_source(self):
        """Test filtrage par source"""
        response = self.client.get('/api/parking_monitor/status/?source=esp32')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Au moins un record avec source esp32
        self.assertGreater(len(response.data['results']), 0)


class ParkingStatusSerializerTest(TestCase):
    """Tests des sérialiseurs"""
    
    def setUp(self):
        self.parking = ParkingStatus.objects.create(
            occupied=7,
            total_spaces=15
        )
    
    def test_serializer_output(self):
        """Test la sérialisation"""
        from .serializers import ParkingStatusSerializer
        
        serializer = ParkingStatusSerializer(self.parking)
        data = serializer.data
        
        self.assertEqual(data['occupied'], 7)
        self.assertEqual(data['available_spaces'], 8)
        self.assertEqual(data['status'], 'available')
        self.assertIn('%', data['occupancy_percentage'])
