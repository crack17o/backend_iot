"""
Script de test pour l'API Parking Intelligence
Utilisation : python test_api.py
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000/api"

def print_header(title):
    """Affiche un header"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")

def test_update_status():
    """Test la mise à jour du statut"""
    print_header("TEST 1 : Mise à jour du statut")
    
    for i in range(3):
        occupied = (i + 1) * 3
        capacity = 20
        
        data = {
            "occupied": occupied,
            "capacity": capacity
        }
        
        print(f"Requête {i+1} : {occupied} places occupées sur {capacity}")
        
        try:
            response = requests.post(f"{API_BASE}/status/update/", json=data, timeout=5)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✓ Succès (201)")
                print(f"  Taux d'occupation : {result['occupancy_rate']}")
                print(f"  Statut : {result['status']}")
            else:
                print(f"✗ Erreur {response.status_code}")
                print(f"  {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"✗ Impossible de se connecter à {API_BASE}")
            return False
        
        except Exception as e:
            print(f"✗ Erreur : {str(e)}")
            return False
        
        time.sleep(1)
    
    return True

def test_get_status():
    """Test la récupération du statut actuel"""
    print_header("TEST 2 : Récupération du statut actuel")
    
    try:
        response = requests.get(f"{API_BASE}/status/", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Succès (200)")
            print(f"  Places occupées : {result['occupied']}")
            print(f"  Places disponibles : {result['available']}")
            print(f"  Capacité : {result['capacity']}")
            print(f"  Taux d'occupation : {result['occupancy_rate']}")
            print(f"  Statut : {result['status']}")
            print(f"  Parking complet ? {result['is_full']}")
            print(f"  Timestamp : {result['timestamp']}")
        else:
            print(f"✗ Erreur {response.status_code}")
            print(f"  {response.text}")
            return False
    
    except Exception as e:
        print(f"✗ Erreur : {str(e)}")
        return False
    
    return True

def test_get_history():
    """Test la récupération de l'historique"""
    print_header("TEST 3 : Récupération de l'historique")
    
    try:
        response = requests.get(f"{API_BASE}/status/history/", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            count = result['count']
            print(f"✓ Succès (200)")
            print(f"  Nombre d'enregistrements : {count}")
            
            if count > 0:
                print(f"\n  Derniers enregistrements :")
                for i, record in enumerate(result['history'][:5], 1):
                    print(f"\n  {i}. {record['timestamp']}")
                    print(f"     Occupés : {record['occupied']}")
                    print(f"     Taux : {record['occupancy_rate']}")
                    print(f"     Statut : {record['status']}")
        else:
            print(f"✗ Erreur {response.status_code}")
            print(f"  {response.text}")
            return False
    
    except Exception as e:
        print(f"✗ Erreur : {str(e)}")
        return False
    
    return True

def test_full_parking():
    """Test avec un parking plein"""
    print_header("TEST 4 : Parking plein")
    
    data = {
        "occupied": 20,
        "capacity": 20
    }
    
    print(f"Envoi : Parking plein (20/20)")
    
    try:
        response = requests.post(f"{API_BASE}/status/update/", json=data, timeout=5)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Succès (201)")
            print(f"  Taux d'occupation : {result['occupancy_rate']}")
            print(f"  Statut : {result['status']}")
            
            if result['status'] == 'full':
                print(f"  ✓ Statut correctement défini à 'full'")
            else:
                print(f"  ✗ Erreur : Statut devrait être 'full'")
                return False
        else:
            print(f"✗ Erreur {response.status_code}")
            return False
    
    except Exception as e:
        print(f"✗ Erreur : {str(e)}")
        return False
    
    return True

def test_invalid_data():
    """Test avec des données invalides"""
    print_header("TEST 5 : Données invalides")
    
    test_cases = [
        ({"occupied": -1, "capacity": 20}, "Occupés négatifs"),
        ({"occupied": 5, "capacity": 0}, "Capacité zéro"),
        ({"occupied": 5, "capacity": -10}, "Capacité négative"),
    ]
    
    for data, description in test_cases:
        print(f"Cas : {description}")
        print(f"  Données : {data}")
        
        try:
            response = requests.post(f"{API_BASE}/status/update/", json=data, timeout=5)
            
            if response.status_code == 400:
                print(f"  ✓ Erreur 400 reçue (comportement attendu)")
            else:
                print(f"  ✗ Erreur : Statut {response.status_code} au lieu de 400")
                return False
        
        except Exception as e:
            print(f"  ✗ Erreur : {str(e)}")
            return False
        
        print()
    
    return True

def main():
    """Exécute tous les tests"""
    print("\n" + "="*50)
    print("  PARKING INTELLIGENCE - API TEST SUITE")
    print("="*50)
    print(f"  API Base : {API_BASE}")
    print(f"  Heure : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier que l'API est accessible
    try:
        response = requests.get(f"{API_BASE}/status/", timeout=5)
        print(f"\n✓ API accessible")
    except:
        print(f"\n✗ API non accessible. Assurez-vous que Django est lancé :")
        print(f"  cd parking && python manage.py runserver")
        return
    
    # Exécuter les tests
    results = [
        ("Mise à jour du statut", test_update_status()),
        ("Récupération du statut", test_get_status()),
        ("Récupération de l'historique", test_get_history()),
        ("Parking plein", test_full_parking()),
        ("Données invalides", test_invalid_data()),
    ]
    
    # Résumé
    print_header("RÉSUMÉ DES TESTS")
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} : {test_name}")
    
    total_pass = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\nTotal : {total_pass}/{total_tests} tests réussis")
    
    if total_pass == total_tests:
        print("\n🎉 Tous les tests sont passés !")
    else:
        print(f"\n⚠️  {total_tests - total_pass} test(s) en échec")

if __name__ == "__main__":
    main()
