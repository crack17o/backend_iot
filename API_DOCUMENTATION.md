# 📡 API Documentation - Système de Parking IoT

## Base URL
```
http://localhost:8000/api
```

---

## 🔐 Authentification

L'API utilise l'authentification par **sessions Django**. Pour les requêtes depuis un navigateur, les sessions sont gérées automatiquement. Pour les requêtes programmatiques, vous pouvez utiliser l'authentification basique ou les sessions.

**Note** : L'endpoint `/api/parking/upload-image/` accepte également une clé API simple via le header `X-API-Key` pour l'authentification des dispositifs ESP32.

---

## 📍 Endpoints Parking

### 1. GET /parking/status/
**Récupère la liste historique du statut du parking (paginée)**

- **Méthode** : GET
- **Authentification** : Requise (sessions)
- **Paramètres de requête** :
  - `page` : Numéro de page (défaut: 1)
  - `page_size` : Taille de page (défaut: 50, max: 100)
  - `timestamp__gte` : Filtrer par date de début (format: YYYY-MM-DD)
  - `timestamp__lte` : Filtrer par date de fin (format: YYYY-MM-DD)
  - `status` : Filtrer par statut (`available` ou `full`)
  - `source` : Filtrer par source (`esp32`, `video`, `api`)

**Réponse réussie (200 OK)**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/parking/status/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:45.123456Z",
      "occupied": 5,
      "available_spaces": 15,
      "total_spaces": 20,
      "occupancy_percentage": "25.0%",
      "occupancy_rate": 25.0,
      "status": "available",
      "source": "esp32",
      "image_path": "uploads/esp32/2024/01/15/esp32_abc123.jpg"
    }
  ]
}
```

---

### 2. GET /parking/status/latest/
**Récupère le dernier statut enregistré du parking**

- **Méthode** : GET
- **Authentification** : Requise

**Réponse réussie (200 OK)**
```json
{
  "id": 1,
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "occupied": 5,
  "available_spaces": 15,
  "total_spaces": 20,
  "occupancy_percentage": "25.0%",
  "occupancy_rate": 25.0,
  "status": "available",
  "source": "esp32",
  "image_path": "uploads/esp32/2024/01/15/esp32_abc123.jpg"
}
```

**Réponse erreur (404 Not Found)**
```json
{
  "error": "Aucune donnée disponible"
}
```

---

### 3. GET /parking/status/stats/
**Récupère les statistiques du parking (dernières 24h)**

- **Méthode** : GET
- **Authentification** : Requise

**Réponse réussie (200 OK)**
```json
{
  "period": "last_24h",
  "total_records": 144,
  "average_occupancy": "45.2%",
  "peak_occupied": 18,
  "times_full": 2,
  "current_status": {
    "occupied": 12,
    "available": 8,
    "status": "available"
  }
}
```

---

### 4. GET /parking/status/export-csv/
**Exporte l'historique du parking en CSV**

- **Méthode** : GET
- **Authentification** : Requise
- **Paramètres de requête** :
  - `start_date` : Date de début (format: YYYY-MM-DD)
  - `end_date` : Date de fin (format: YYYY-MM-DD)

**Réponse** : Fichier CSV téléchargeable

---

### 5. GET /parking/status/export-pdf/
**Exporte un rapport PDF de l'historique du parking**

- **Méthode** : GET
- **Authentification** : Requise
- **Paramètres de requête** :
  - `start_date` : Date de début (format: YYYY-MM-DD)
  - `end_date` : Date de fin (format: YYYY-MM-DD)

**Réponse** : Fichier PDF téléchargeable

---

### 6. POST /parking/upload-image/
**Upload une image depuis ESP32-CAM et détecte les voitures**

- **Méthode** : POST
- **Authentification** : aucune (pour usage local et tests)
- **Content-Type** : `multipart/form-data`

**Body (Form-data)**
- `image` : Fichier image (JPEG, PNG, max 10MB)

**Réponse réussie (201 Created)**
```json
{
  "id": 1,
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "occupied": 5,
  "available_spaces": 15,
  "total_spaces": 20,
  "occupancy_percentage": "25.0%",
  "occupancy_rate": 25.0,
  "status": "available",
  "source": "esp32",
  "image_path": "uploads/esp32/2024/01/15/esp32_abc123.jpg",
  "detected_count": 5
}
```

**Réponse erreur (400 Bad Request)**
```json
{
  "error": "Aucune image fournie"
}
```

---

### 7. POST /parking/update/
**Mise à jour manuelle du statut du parking**

- **Méthode** : POST
- **Authentification** : Requise (sessions)
- **Content-Type** : `application/json`

**Body (JSON)**
```json
{
  "occupied": 5,
  "total_spaces": 20
}
```

**Paramètres**
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| occupied | integer | Oui | Nombre de places occupées (>= 0) |
| total_spaces | integer | Non | Capacité totale (défaut: 20) |

**Réponse réussie (201 Created)**
```json
{
  "id": 1,
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "occupied": 5,
  "available_spaces": 15,
  "total_spaces": 20,
  "occupancy_percentage": "25.0%",
  "occupancy_rate": 25.0,
  "status": "available",
  "source": "esp32"
}
```

---

## 🚦 Endpoints Trafic

### 8. GET /traffic/routes/
**Liste toutes les routes (trajets) actives**

- **Méthode** : GET
- **Authentification** : Requise
- **Paramètres de requête** :
  - `page` : Numéro de page
  - `page_size` : Taille de page
  - `direction` : Filtrer par direction (`aller`, `retour`, `aller_retour`)

**Réponse réussie (200 OK)**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Maison - Travail",
      "description": "Trajet quotidien",
      "start_latitude": 48.8566,
      "start_longitude": 2.3522,
      "end_latitude": 48.8606,
      "end_longitude": 2.3376,
      "direction": "aller_retour",
      "is_active": true,
      "created_at": "2024-01-15T08:00:00Z",
      "updated_at": "2024-01-15T08:00:00Z"
    }
  ]
}
```

---

### 9. POST /traffic/routes/
**Crée une nouvelle route**

- **Méthode** : POST
- **Authentification** : Requise
- **Content-Type** : `application/json`

**Body (JSON)**
```json
{
  "name": "Maison - Travail",
  "description": "Trajet quotidien",
  "start_latitude": 48.8566,
  "start_longitude": 2.3522,
  "end_latitude": 48.8606,
  "end_longitude": 2.3376,
  "direction": "aller_retour"
}
```

**Paramètres**
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| name | string | Oui | Nom de la route |
| description | string | Non | Description |
| start_latitude | float | Oui | Latitude du point de départ |
| start_longitude | float | Oui | Longitude du point de départ |
| end_latitude | float | Oui | Latitude du point d'arrivée |
| end_longitude | float | Oui | Longitude du point d'arrivée |
| direction | string | Non | `aller`, `retour`, ou `aller_retour` (défaut) |

**Réponse réussie (201 Created)**
```json
{
  "id": 1,
  "name": "Maison - Travail",
  "description": "Trajet quotidien",
  "start_latitude": 48.8566,
  "start_longitude": 2.3522,
  "end_latitude": 48.8606,
  "end_longitude": 2.3376,
  "direction": "aller_retour",
  "is_active": true,
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

---

### 10. GET /traffic/routes/<id>/
**Récupère les détails d'une route**

- **Méthode** : GET
- **Authentification** : Requise

**Réponse réussie (200 OK)**
```json
{
  "id": 1,
  "name": "Maison - Travail",
  "description": "Trajet quotidien",
  "start_latitude": 48.8566,
  "start_longitude": 2.3522,
  "end_latitude": 48.8606,
  "end_longitude": 2.3376,
  "direction": "aller_retour",
  "is_active": true,
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

---

### 11. PUT /traffic/routes/<id>/
**Met à jour une route**

- **Méthode** : PUT
- **Authentification** : Requise
- **Content-Type** : `application/json`

**Body (JSON)** : Même format que POST, tous les champs optionnels

---

### 12. DELETE /traffic/routes/<id>/
**Supprime une route (désactive)**

- **Méthode** : DELETE
- **Authentification** : Requise

**Réponse réussie (204 No Content)**

---

### 13. POST /traffic/routes/<id>/check-traffic/
**Vérifie l'état du trafic pour une route et enregistre le résultat**

- **Méthode** : POST
- **Authentification** : Requise

**Réponse réussie (201 Created)**
```json
{
  "id": 1,
  "route": 1,
  "route_name": "Maison - Travail",
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "duration_seconds": 1200,
  "duration_minutes": 20.0,
  "duration_in_traffic_seconds": 1800,
  "duration_in_traffic_minutes": 30.0,
  "distance_meters": 5000,
  "distance_km": 5.0,
  "traffic_status": "embouteillage",
  "delay_seconds": 600,
  "delay_minutes": 10.0,
  "delay_percentage": 50.0
}
```

**Statuts de trafic possibles** :
- `fluide` : < 10% de retard
- `modere` : 10-30% de retard
- `embouteillage` : 30-50% de retard
- `bloque` : ≥ 50% de retard

---

### 14. GET /traffic/status/
**Liste l'historique complet des statuts de trafic**

- **Méthode** : GET
- **Authentification** : Requise
- **Paramètres de requête** :
  - `page` : Numéro de page
  - `page_size` : Taille de page
  - `traffic_status` : Filtrer par statut (`fluide`, `modere`, `embouteillage`, `bloque`)
  - `route` : Filtrer par ID de route

**Réponse réussie (200 OK)**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "route": 1,
      "route_name": "Maison - Travail",
      "timestamp": "2024-01-15T10:30:45Z",
      "duration_seconds": 1200,
      "duration_minutes": 20.0,
      "duration_in_traffic_seconds": 1800,
      "duration_in_traffic_minutes": 30.0,
      "distance_meters": 5000,
      "distance_km": 5.0,
      "traffic_status": "embouteillage",
      "delay_seconds": 600,
      "delay_minutes": 10.0,
      "delay_percentage": 50.0
    }
  ]
}
```

---

### 15. GET /traffic/status/latest/
**Récupère le dernier statut de trafic pour chaque route active**

- **Méthode** : GET
- **Authentification** : Requise

**Réponse réussie (200 OK)**
```json
[
  {
    "id": 1,
    "route": 1,
    "route_name": "Maison - Travail",
    "timestamp": "2024-01-15T10:30:45Z",
    "duration_minutes": 20.0,
    "duration_in_traffic_minutes": 30.0,
    "distance_km": 5.0,
    "traffic_status": "embouteillage",
    "delay_minutes": 10.0,
    "delay_percentage": 50.0
  }
]
```

---

### 16. GET /traffic/status/route/<route_id>/
**Récupère l'historique du trafic pour une route spécifique**

- **Méthode** : GET
- **Authentification** : Requise

**Réponse réussie (200 OK)** : Liste paginée des statuts de trafic pour cette route

---

### 17. POST /traffic/check/
**Vérifie le trafic entre deux points GPS (sans créer de route)**

- **Méthode** : POST
- **Authentification** : Requise
- **Content-Type** : `application/json`

**Body (JSON)**
```json
{
  "start_latitude": 48.8566,
  "start_longitude": 2.3522,
  "end_latitude": 48.8606,
  "end_longitude": 2.3376
}
```

**Paramètres**
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| start_latitude | float | Oui | Latitude du point de départ |
| start_longitude | float | Oui | Longitude du point de départ |
| end_latitude | float | Oui | Latitude du point d'arrivée |
| end_longitude | float | Oui | Longitude du point d'arrivée |

**Réponse réussie (200 OK)**
```json
{
  "duration_minutes": 20.0,
  "duration_in_traffic_minutes": 30.0,
  "distance_km": 5.0,
  "delay_minutes": 10.0,
  "delay_percentage": 50.0,
  "traffic_status": "embouteillage",
  "has_congestion": true
}
```

---

## 📊 Champs de réponse

### Parking Status
| Champ | Type | Description |
|-------|------|-------------|
| id | integer | Identifiant unique |
| timestamp | string | Date/heure ISO 8601 |
| occupied | integer | Nombre de places occupées |
| available_spaces | integer | Nombre de places disponibles |
| total_spaces | integer | Capacité totale (20) |
| occupancy_percentage | string | Pourcentage formaté (ex: "25.0%") |
| occupancy_rate | float | Pourcentage numérique |
| status | string | `available` ou `full` |
| source | string | `esp32`, `video`, ou `api` |
| image_path | string | Chemin de l'image (si disponible) |

### Traffic Status
| Champ | Type | Description |
|-------|------|-------------|
| id | integer | Identifiant unique |
| route | integer | ID de la route |
| route_name | string | Nom de la route |
| timestamp | string | Date/heure ISO 8601 |
| duration_seconds | integer | Durée sans trafic (secondes) |
| duration_minutes | float | Durée sans trafic (minutes) |
| duration_in_traffic_seconds | integer | Durée avec trafic (secondes) |
| duration_in_traffic_minutes | float | Durée avec trafic (minutes) |
| distance_meters | integer | Distance en mètres |
| distance_km | float | Distance en kilomètres |
| traffic_status | string | `fluide`, `modere`, `embouteillage`, `bloque` |
| delay_seconds | integer | Délai dû au trafic (secondes) |
| delay_minutes | float | Délai dû au trafic (minutes) |
| delay_percentage | float | Pourcentage de retard |

---

## 🔢 Codes de statut HTTP

| Code | Signification |
|------|---------------|
| 200 | Requête réussie (GET) |
| 201 | Ressource créée (POST) |
| 204 | Ressource supprimée (DELETE) |
| 400 | Requête invalide (paramètres manquants/incorrects) |
| 401 | Non authentifié |
| 403 | Permission refusée |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |

---

## 📝 Exemples de requêtes

### JavaScript/Fetch API

```javascript
// Obtenir le statut actuel du parking
fetch('http://localhost:8000/api/parking/status/latest/', {
  credentials: 'include'  // Pour les sessions
})
  .then(res => res.json())
  .then(data => console.log(data));

// Upload d'image depuis ESP32
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8000/api/parking/upload-image/', {
  method: 'POST',
  headers: {
    'X-API-Key': 'VOTRE_CLE_ESP32'
  },
  body: formData
})
  .then(res => res.json())
  .then(data => console.log(data));

// Vérifier le trafic
fetch('http://localhost:8000/api/traffic/check/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include',
  body: JSON.stringify({
    start_latitude: 48.8566,
    start_longitude: 2.3522,
    end_latitude: 48.8606,
    end_longitude: 2.3376
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Python/Requests

```python
import requests

# Session pour l'authentification
session = requests.Session()

# Obtenir le statut actuel
response = session.get('http://localhost:8000/api/parking/status/latest/')
print(response.json())

# Upload d'image
with open('image.jpg', 'rb') as f:
    files = {'image': f}
    headers = {'X-API-Key': 'VOTRE_CLE_ESP32'}
    response = requests.post(
        'http://localhost:8000/api/parking/upload-image/',
        files=files,
        headers=headers
    )
    print(response.json())

# Vérifier le trafic
response = session.post(
    'http://localhost:8000/api/traffic/check/',
    json={
        'start_latitude': 48.8566,
        'start_longitude': 2.3522,
        'end_latitude': 48.8606,
        'end_longitude': 2.3376
    }
)
print(response.json())
```

### cURL

```bash
# Obtenir le statut actuel
curl -X GET http://localhost:8000/api/parking/status/latest/ \
  --cookie-jar cookies.txt --cookie cookies.txt

# Upload d'image
curl -X POST http://localhost:8000/api/parking/upload-image/ \
  -H "X-API-Key: VOTRE_CLE_ESP32" \
  -F "image=@photo.jpg"

# Créer une route
curl -X POST http://localhost:8000/api/traffic/routes/ \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt --cookie cookies.txt \
  -d '{
    "name": "Maison - Travail",
    "start_latitude": 48.8566,
    "start_longitude": 2.3522,
    "end_latitude": 48.8606,
    "end_longitude": 2.3376
  }'

# Vérifier le trafic
curl -X POST http://localhost:8000/api/traffic/check/ \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt --cookie cookies.txt \
  -d '{
    "start_latitude": 48.8566,
    "start_longitude": 2.3522,
    "end_latitude": 48.8606,
    "end_longitude": 2.3376
  }'
```

---

## 🔧 Configuration

### Clé API ESP32
Configurez `ESP32_API_KEY` dans `parking/parking_monitor/utils/constants.py`

### Clé API Google Maps
1. Obtenez une clé API depuis [Google Cloud Console](https://console.cloud.google.com/)
2. Activez l'API "Directions API"
3. Configurez `GOOGLE_MAPS_API_KEY` dans `parking/parking_monitor/utils/constants.py`

---

## ⚠️ Limitations et quotas

- **Historique parking** : Pagination automatique (50 par page, max 100)
- **Upload images** : Taille max 10MB
- **Google Maps API** : Sujet aux quotas de votre plan Google Cloud
- **Fréquence recommandée** : 
  - Parking : Toutes les 10 secondes
  - Trafic : Toutes les 5-10 minutes (selon vos besoins)

---

## 🐛 Dépannage

### Erreur: "Clé API Google Maps non configurée"
- Vérifiez que `GOOGLE_MAPS_API_KEY` est configurée dans `constants.py`
- Vérifiez que la clé API est valide et que l'API Directions est activée

### Erreur: "Aucun itinéraire trouvé"
- Vérifiez que les coordonnées GPS sont valides
- Vérifiez que les points de départ et d'arrivée sont accessibles en voiture

### Erreur: "Permission denied"
- Vérifiez que vous êtes authentifié (sessions)
- Vérifiez que vous avez les permissions nécessaires

---

**API Version** : 2.0  
**Dernière mise à jour** : Janvier 2026
