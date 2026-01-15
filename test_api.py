"""
Script de test pour les API du système de parking
Usage: python test_api.py
"""

import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Affiche un séparateur de section"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(method, endpoint, status_code, data):
    """Affiche une réponse formatée"""
    print(f"\n{method} {endpoint}")
    print(f"Status: {status_code}")
    if data:
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")


def test_server_connection():
    """Vérifie que le serveur Django est accessible"""
    try:
        response = requests.get(f"{BASE_URL}/status/", timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Le serveur Django n'est pas accessible!")
        print("   Assurez-vous que le serveur est démarré:")
        print("   python manage.py runserver")
        return False
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False


def test_get_latest():
    """Test GET /api/status/latest/"""
    print_section("TEST 1: Dernier statut")
    try:
        response = requests.get(f"{BASE_URL}/status/latest/")
        data = response.json() if response.status_code == 200 else None
        print_response("GET", "/status/latest/", response.status_code, data)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_get_stats():
    """Test GET /api/status/stats/"""
    print_section("TEST 2: Statistiques (24h)")
    try:
        response = requests.get(f"{BASE_URL}/status/stats/")
        data = response.json() if response.status_code in [200, 404] else None
        print_response("GET", "/status/stats/", response.status_code, data)
        return response.status_code in [200, 404]  # 404 si pas de données
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_get_history():
    """Test GET /api/status/ avec pagination"""
    print_section("TEST 3: Historique (paginé)")
    try:
        response = requests.get(
            f"{BASE_URL}/status/",
            params={"page_size": 5}
        )
        data = response.json()
        print_response("GET", "/status/?page_size=5", response.status_code, data)
        if response.status_code == 200 and 'count' in data:
            print(f"\n✓ Total d'enregistrements: {data.get('count', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_get_history_filtered():
    """Test GET /api/status/ avec filtres"""
    print_section("TEST 4: Historique filtré")
    try:
        # Trier par taux d'occupation décroissant
        response = requests.get(
            f"{BASE_URL}/status/",
            params={"ordering": "-occupancy_rate", "page_size": 3}
        )
        data = response.json()
        print_response("GET", "/status/?ordering=-occupancy_rate", 
                      response.status_code, data)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_post_update():
    """Test POST /api/update/"""
    print_section("TEST 5: Mise à jour manuelle")
    try:
        data = {
            "occupied": 8,
            "total_spaces": 15
        }
        response = requests.post(
            f"{BASE_URL}/update/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response_data = response.json() if response.status_code in [201, 400] else None
        print_response("POST", "/update/", response.status_code, response_data)
        
        if response.status_code == 201:
            print(f"\n✓ Statut créé: {response_data.get('occupied', 'N/A')}/{response_data.get('total_spaces', 'N/A')} places")
            print(f"  Taux d'occupation: {response_data.get('occupancy_rate', 'N/A'):.1f}%")
        
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_post_update_invalid():
    """Test POST /api/update/ avec données invalides"""
    print_section("TEST 6: Mise à jour avec erreurs (test de validation)")
    try:
        # Test avec données invalides (occupied négatif)
        data = {
            "occupied": -5,
            "total_spaces": 15
        }
        response = requests.post(
            f"{BASE_URL}/update/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response_data = response.json() if response.status_code == 400 else None
        print_response("POST", "/update/ (données invalides)", 
                      response.status_code, response_data)
        
        if response.status_code == 400:
            print("\n✓ Validation fonctionne: erreur 400 attendue")
        
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_post_upload_image(image_path=None):
    """Test POST /api/upload-image/"""
    print_section("TEST 7: Upload d'image")
    
    # Si aucun chemin fourni, chercher une image de test
    if not image_path:
        # Chercher des images communes dans le projet
        test_images = [
            Path("test_image.jpg"),
            Path("sample.jpg"),
            Path("images/test.jpg"),
        ]
        
        for img_path in test_images:
            if img_path.exists():
                image_path = img_path
                break
    
    if not image_path or not Path(image_path).exists():
        print("⚠ Image de test non trouvée. Test ignoré.")
        print("  Pour tester: python test_api.py <chemin_image.jpg>")
        return None
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (Path(image_path).name, f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/upload-image/",
                files=files
            )
        
        response_data = response.json() if response.status_code in [201, 400] else None
        print_response("POST", "/upload-image/", response.status_code, response_data)
        
        if response.status_code == 201:
            print(f"\n✓ Image uploadée: {response_data.get('detected_count', 'N/A')} voitures détectées")
        
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("  TESTS DES API - SYSTÈME DE PARKING")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print("\n⚠ Assurez-vous que le serveur Django est démarré!")
    print("   python manage.py runserver\n")
    
    # Vérifier la connexion au serveur
    if not test_server_connection():
        sys.exit(1)
    
    # Récupérer le chemin de l'image si fourni en argument
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Liste des tests à exécuter
    tests = [
        ("Dernier statut", test_get_latest),
        ("Statistiques", test_get_stats),
        ("Historique", test_get_history),
        ("Historique filtré", test_get_history_filtered),
        ("Mise à jour manuelle", test_post_update),
        ("Validation des erreurs", test_post_update_invalid),
        ("Upload d'image", lambda: test_post_upload_image(image_path)),
    ]
    
    # Exécuter les tests
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erreur dans {name}: {e}")
            results.append((name, False))
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for name, result in results:
        if result is True:
            print(f"✓ {name}")
        elif result is False:
            print(f"✗ {name}")
        else:
            print(f"- {name} (ignoré)")
    
    print(f"\nRésultats: {passed} réussis, {failed} échoués, {skipped} ignorés")
    
    if failed > 0:
        print("\n⚠ Certains tests ont échoué. Vérifiez les logs ci-dessus.")
        sys.exit(1)
    else:
        print("\n✓ Tous les tests sont passés avec succès!")


if __name__ == "__main__":
    main()
