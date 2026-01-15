# Guide de test des API - Système de Parking

## 📋 Endpoints disponibles

Base URL: `http://localhost:8000/api/`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/status/` | Liste de l'historique (paginé) |
| GET | `/api/status/{id}/` | Détails d'une entrée spécifique |
| GET | `/api/status/latest/` | Dernier statut enregistré |
| GET | `/api/status/stats/` | Statistiques des 24 dernières heures |
| POST | `/api/upload-image/` | Upload image ESP32-CAM pour détection |
| POST | `/api/update/` | Mise à jour manuelle du statut |

---

## 🚀 Méthode 1 : Interface Django REST Framework (Browsable API)

**La plus simple pour démarrer !**

1. Démarrer le serveur Django :
```bash
python manage.py runserver
```

2. Ouvrir dans votre navigateur :
- http://localhost:8000/api/status/
- http://localhost:8000/api/status/latest/
- http://localhost:8000/api/status/stats/

**Avantages :** Interface visuelle, formulaires pour tester POST, pas d'outil externe requis.

---

## 📝 Méthode 2 : curl (Ligne de commande)

### GET - Liste de l'historique
```bash
curl http://localhost:8000/api/status/
```

### GET - Dernier statut
```bash
curl http://localhost:8000/api/status/latest/
```

### GET - Statistiques
```bash
curl http://localhost:8000/api/status/stats/
```

### GET - Avec filtres et pagination
```bash
# Filtrer par statut
curl "http://localhost:8000/api/status/?status=full"

# Trier par taux d'occupation
curl "http://localhost:8000/api/status/?ordering=occupancy_rate"

# Pagination
curl "http://localhost:8000/api/status/?page=2&page_size=10"
```

### POST - Mise à jour manuelle
```bash
curl -X POST http://localhost:8000/api/update/ \
  -H "Content-Type: application/json" \
  -d '{"occupied": 5, "total_spaces": 15}'
```

### POST - Upload d'image
```bash
curl -X POST http://localhost:8000/api/upload-image/ \
  -F "image=@/chemin/vers/votre/image.jpg"
```

**Format Windows PowerShell :**
```powershell
curl.exe -X POST http://localhost:8000/api/upload-image/ `
  -F "image=@C:\Users\VotreNom\image.jpg"
```

---

## 🔧 Méthode 3 : Python requests (Script de test)

Créez un fichier `test_api.py` :

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_get_latest():
    """Test GET /api/status/latest/"""
    response = requests.get(f"{BASE_URL}/status/latest/")
    print("GET /status/latest/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_get_stats():
    """Test GET /api/status/stats/"""
    response = requests.get(f"{BASE_URL}/status/stats/")
    print("GET /status/stats/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_post_update():
    """Test POST /api/update/"""
    data = {
        "occupied": 8,
        "total_spaces": 15
    }
    response = requests.post(
        f"{BASE_URL}/update/",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print("POST /update/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_post_upload_image(image_path):
    """Test POST /api/upload-image/"""
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(
            f"{BASE_URL}/upload-image/",
            files=files
        )
    print("POST /upload-image/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_get_history():
    """Test GET /api/status/ avec pagination"""
    response = requests.get(
        f"{BASE_URL}/status/",
        params={"page_size": 5}
    )
    print("GET /status/ (paginated)")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total results: {data.get('count', 'N/A')}")
    print(f"Results: {json.dumps(data.get('results', []), indent=2)}")
    print("-" * 50)

if __name__ == "__main__":
    print("=" * 50)
    print("TEST DES API - SYSTÈME DE PARKING")
    print("=" * 50)
    print()
    
    # Tests GET
    test_get_latest()
    test_get_stats()
    test_get_history()
    
    # Test POST - Mise à jour manuelle
    test_post_update()
    
    # Test POST - Upload image (décommentez et ajoutez le chemin)
    # test_post_upload_image("chemin/vers/image.jpg")
```

**Exécution :**
```bash
python test_api.py
```

---

## 📮 Méthode 4 : Postman / Insomnia

### ⚡ Démarrage rapide avec Postman

**Importation automatique (recommandé) :**

1. **Ouvrir Postman**
2. **Cliquer sur "Import"** (en haut à gauche)
3. **Sélectionner le fichier** `Parking_API.postman_collection.json`
4. **La collection est prête !** 🎉

La collection inclut :
- ✅ Toutes les requêtes préconfigurées
- ✅ Variables d'environnement (`base_url`)
- ✅ Exemples de body JSON
- ✅ Tests d'erreurs

### Configuration manuelle Postman

Si vous préférez créer la collection manuellement :

1. **Créer une nouvelle collection** : "Parking API"

2. **Créer un environnement** (optionnel mais recommandé) :
   - Cliquez sur "Environments" dans le panneau gauche
   - Créez un nouvel environnement "Parking Local"
   - Ajoutez la variable :
     - Variable: `base_url`
     - Valeur initiale: `http://localhost:8000/api`
     - Valeur actuelle: `http://localhost:8000/api`
   - Sélectionnez cet environnement dans le menu déroulant en haut à droite

3. **Variables de collection** :
   - Ouvrez la collection → Onglet "Variables"
   - Variable: `base_url` = `http://localhost:8000/api`

4. **Requêtes à créer** :

#### GET Latest Status
- **Méthode:** GET
- **URL:** `{{base_url}}/status/latest/`
- **Headers:** (aucun requis)

#### GET Statistics
- **Méthode:** GET
- **URL:** `{{base_url}}/status/stats/`

#### GET History
- **Méthode:** GET
- **URL:** `{{base_url}}/status/`
- **Params:**
  - `page`: 1
  - `page_size`: 10
  - `status`: full (optionnel)
  - `ordering`: -timestamp (optionnel)

#### POST Manual Update
- **Méthode:** POST
- **URL:** `{{base_url}}/update/`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "occupied": 10,
  "total_spaces": 15
}
```

#### POST Upload Image
- **Méthode:** POST
- **URL:** `{{base_url}}/upload-image/`
- **Body (form-data):**
  - Key: `image` (Type: File)
  - Value: Sélectionner un fichier image

### 📋 Liste complète des requêtes dans la collection

La collection Postman `Parking_API.postman_collection.json` contient :

#### 📊 Statut (6 requêtes)
1. **GET - Dernier statut** - `{{base_url}}/status/latest/`
2. **GET - Statistiques (24h)** - `{{base_url}}/status/stats/`
3. **GET - Historique (paginated)** - `{{base_url}}/status/?page=1&page_size=10`
4. **GET - Historique filtré par statut** - `{{base_url}}/status/?status=full&page_size=5`
5. **GET - Historique trié** - `{{base_url}}/status/?ordering=-occupancy_rate&page_size=5`
6. **GET - Détail d'un enregistrement** - `{{base_url}}/status/1/`

#### ✏️ Mise à jour (3 requêtes)
7. **POST - Mise à jour manuelle** - `{{base_url}}/update/` (occupied: 8)
8. **POST - Mise à jour (parking plein)** - `{{base_url}}/update/` (occupied: 15)
9. **POST - Mise à jour (parking vide)** - `{{base_url}}/update/` (occupied: 0)

#### 📤 Upload Image (1 requête)
10. **POST - Upload image ESP32-CAM** - `{{base_url}}/upload-image/`

#### 🧪 Tests d'erreurs (4 requêtes)
11. **POST - Erreur validation (occupied négatif)** - Test 400
12. **POST - Erreur validation (données manquantes)** - Test 400
13. **POST - Erreur upload (sans image)** - Test 400
14. **GET - Erreur 404 (ID inexistant)** - Test 404

### 💡 Conseils d'utilisation Postman

1. **Tester dans l'ordre** :
   - Commencez par "GET - Dernier statut" pour vérifier que le serveur répond
   - Ensuite "POST - Mise à jour manuelle" pour créer des données
   - Puis "GET - Historique" pour voir vos données

2. **Variables dynamiques** :
   - Les requêtes utilisent `{{base_url}}` qui pointe vers `http://localhost:8000/api`
   - Vous pouvez changer facilement pour un serveur de production

3. **Tests automatiques** (optionnel) :
   - Ajoutez des scripts de test dans l'onglet "Tests" de chaque requête
   - Exemple pour vérifier le statut 200 :
   ```javascript
   pm.test("Status code is 200", function () {
       pm.response.to.have.status(200);
   });
   ```

4. **Environnements multiples** :
   - Créez des environnements pour : Local, Dev, Production
   - Changez facilement entre eux avec le menu déroulant

### Insomnia

Configuration similaire à Postman. Vous pouvez :
- Importer la collection Postman dans Insomnia
- Ou créer manuellement les requêtes en suivant la même structure
- Configurer :
  - Méthode HTTP
  - URL avec variables
  - Headers (si nécessaire)
  - Body (JSON ou form-data pour upload)

---

## 🧪 Méthode 5 : Tests unitaires Django

Créez un fichier `parking_monitor/tests/test_api.py` :

```python
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from parking_monitor.models import ParkingStatus
import json


class ParkingAPITestCase(TestCase):
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()
        # Créer quelques données de test
        ParkingStatus.objects.create(
            occupied=5,
            total_spaces=15,
            source='api'
        )
        ParkingStatus.objects.create(
            occupied=15,
            total_spaces=15,
            source='api'
        )

    def test_get_latest_status(self):
        """Test GET /api/status/latest/"""
        url = reverse('parking_monitor:parking-status-latest')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('occupied', response.data)
        self.assertIn('available', response.data)
        self.assertIn('status', response.data)

    def test_get_stats(self):
        """Test GET /api/status/stats/"""
        url = reverse('parking_monitor:parking-status-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_occupancy', response.data)
        self.assertIn('total_records', response.data)

    def test_post_manual_update(self):
        """Test POST /api/update/"""
        url = reverse('parking_monitor:update-manual')
        data = {
            "occupied": 8,
            "total_spaces": 15
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['occupied'], 8)
        self.assertEqual(response.data['available'], 7)

    def test_get_history_pagination(self):
        """Test GET /api/status/ avec pagination"""
        url = reverse('parking_monitor:parking-status-list')
        response = self.client.get(url, {'page_size': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_filter_by_status(self):
        """Test filtrage par statut"""
        url = reverse('parking_monitor:parking-status-list')
        response = self.client.get(url, {'status': 'full'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérifier que tous les résultats sont "full"
        for result in response.data.get('results', []):
            self.assertEqual(result['status'], 'full')
```

**Exécution des tests :**
```bash
python manage.py test parking_monitor.tests.test_api
```

---

## 🔍 Méthode 6 : Vérification des erreurs

### Tester les erreurs 400 (Bad Request)

```bash
# POST sans données
curl -X POST http://localhost:8000/api/update/ \
  -H "Content-Type: application/json"

# POST avec données invalides
curl -X POST http://localhost:8000/api/update/ \
  -H "Content-Type: application/json" \
  -d '{"occupied": -5}'
```

### Tester les erreurs 404 (Not Found)

```bash
# ID inexistant
curl http://localhost:8000/api/status/99999/
```

### Tester les erreurs 500 (Server Error)

Vérifiez les logs Django pour voir les détails des erreurs.

---

## 📊 Exemples de réponses

### GET /api/status/latest/
```json
{
  "id": 1,
  "timestamp": "2024-01-14T10:30:45.123456Z",
  "occupied": 5,
  "total_spaces": 15,
  "available": 10,
  "status": "available",
  "occupancy_rate": 33.3,
  "image_path": "",
  "source": "esp32"
}
```

### GET /api/status/stats/
```json
{
  "period": "last_24h",
  "total_records": 48,
  "average_occupancy": "45.2%",
  "peak_occupied": 15,
  "times_full": 3,
  "current_status": {
    "occupied": 8,
    "available": 7,
    "status": "available"
  }
}
```

### POST /api/update/ (Response 201)
```json
{
  "id": 10,
  "timestamp": "2024-01-14T10:35:00.123456Z",
  "occupied": 8,
  "total_spaces": 15,
  "available": 7,
  "status": "available",
  "occupancy_rate": 53.3,
  "image_path": null,
  "source": "api"
}
```

---

## 💡 Conseils

1. **Toujours démarrer le serveur Django** avant de tester :
   ```bash
   python manage.py runserver
   ```

2. **Vérifier que la base de données est configurée** et que les migrations sont appliquées :
   ```bash
   python manage.py migrate
   ```

3. **Pour tester l'upload d'image**, utilisez une vraie image JPEG :
   - Format supporté : JPG, JPEG
   - Taille max : configurée dans `constants.py`

4. **Utiliser les logs Django** pour déboguer :
   - Les erreurs apparaissent dans la console du serveur
   - Activez `DEBUG=True` dans `settings.py` pour plus de détails

5. **Tester en environnement de développement** avant la production

---

## 🐛 Débogage

### Problème : 404 Not Found
- Vérifiez que le serveur Django est démarré
- Vérifiez l'URL (doit commencer par `/api/`)
- Vérifiez que les migrations sont appliquées

### Problème : 500 Internal Server Error
- Vérifiez les logs du serveur Django
- Vérifiez la configuration de la base de données
- Vérifiez que tous les packages sont installés

### Problème : CORS errors (si test depuis navigateur/externe)
- Installez `django-cors-headers`
- Configurez CORS dans `settings.py`
