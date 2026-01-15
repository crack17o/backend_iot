# API Documentation - Parking Intelligence

## Base URL
```
http://localhost:8000/api
```

## Endpoints disponibles

### 1. GET /status/
**Récupère le statut actuel du parking**

- **Méthode** : GET
- **Authentification** : Aucune
- **Paramètres** : Aucun

**Réponse réussie (200 OK)**
```json
{
    "occupied": 5,
    "available": 15,
    "capacity": 20,
    "occupancy_rate": "25.0%",
    "status": "available",
    "is_full": false,
    "timestamp": "2024-01-14T10:30:45.123456Z"
}
```

**Réponse erreur (404 Not Found)**
```json
{
    "error": "No parking status data available"
}
```

---

### 2. POST /status/update/
**Met à jour le statut du parking**

- **Méthode** : POST
- **Authentification** : Aucune
- **Content-Type** : application/json

**Body (JSON)**
```json
{
    "occupied": 5,
    "capacity": 20
}
```

**Paramètres**
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| occupied | integer | Oui | Nombre de places occupées (>= 0) |
| capacity | integer | Oui | Capacité totale du parking (> 0) |

**Réponse réussie (201 Created)**
```json
{
    "success": true,
    "id": 1,
    "timestamp": "2024-01-14T10:30:45.123456Z",
    "occupied": 5,
    "available": 15,
    "capacity": 20,
    "occupancy_rate": "25.0%",
    "status": "available"
}
```

**Réponse erreur (400 Bad Request)**
```json
{
    "error": "Invalid values. occupied >= 0 and capacity > 0"
}
```

---

### 3. GET /status/history/
**Récupère l'historique des statuts du parking**

- **Méthode** : GET
- **Authentification** : Aucune
- **Paramètres** : Aucun
- **Limite** : 100 derniers enregistrements

**Réponse réussie (200 OK)**
```json
{
    "count": 50,
    "history": [
        {
            "timestamp": "2024-01-14T10:35:45.123456Z",
            "occupied": 12,
            "available": 8,
            "occupancy_rate": "60.0%",
            "status": "available"
        },
        {
            "timestamp": "2024-01-14T10:30:45.123456Z",
            "occupied": 5,
            "available": 15,
            "occupancy_rate": "25.0%",
            "status": "available"
        }
    ]
}
```

---

## Champs de réponse

| Champ | Type | Description |
|-------|------|-------------|
| occupied | integer | Nombre de places occupées |
| available | integer | Nombre de places disponibles |
| capacity | integer | Capacité totale du parking |
| occupancy_rate | string | Pourcentage d'occupation (ex: "25.0%") |
| status | string | "available" ou "full" |
| is_full | boolean | true si le parking est plein |
| timestamp | string | ISO 8601 datetime |

---

## Codes de statut HTTP

| Code | Signification |
|------|---------------|
| 200 | Requête réussie (GET) |
| 201 | Ressource créée (POST) |
| 400 | Requête invalide (paramètres manquants/incorrects) |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |

---

## Exemples de requêtes

### JavaScript/Fetch API

```javascript
// Obtenir le statut actuel
fetch('http://localhost:8000/api/status/')
    .then(res => res.json())
    .then(data => console.log(data));

// Mettre à jour le statut
fetch('http://localhost:8000/api/status/update/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        occupied: 5,
        capacity: 20
    })
})
    .then(res => res.json())
    .then(data => console.log(data));

// Obtenir l'historique
fetch('http://localhost:8000/api/status/history/')
    .then(res => res.json())
    .then(data => console.log(data));
```

### Python/Requests

```python
import requests

# Obtenir le statut actuel
response = requests.get('http://localhost:8000/api/status/')
print(response.json())

# Mettre à jour le statut
response = requests.post('http://localhost:8000/api/status/update/', json={
    'occupied': 5,
    'capacity': 20
})
print(response.json())

# Obtenir l'historique
response = requests.get('http://localhost:8000/api/status/history/')
print(response.json())
```

### cURL

```bash
# Obtenir le statut actuel
curl -X GET http://localhost:8000/api/status/

# Mettre à jour le statut
curl -X POST http://localhost:8000/api/status/update/ \
  -H "Content-Type: application/json" \
  -d '{"occupied": 5, "capacity": 20}'

# Obtenir l'historique
curl -X GET http://localhost:8000/api/status/history/
```

---

## Règles métier

1. **occupied >= 0** : Le nombre de places occupées doit être positif ou nul
2. **capacity > 0** : La capacité doit être strictement positive
3. **status = "full"** si `occupied >= capacity`
4. **status = "available"** si `occupied < capacity`
5. **occupancy_rate** = `(occupied / capacity * 100)`

---

## Limitations et quotas

- **Historique** : Les 100 derniers enregistrements sont disponibles
- **Fréquence de mise à jour recommandée** : Toutes les 10 secondes
- **Rétention des données** : Pas de limite (à configurer selon vos besoins)

---

## À faire

- [ ] Ajouter l'authentification par token
- [ ] Implémenter un système de pagination
- [ ] Ajouter des filtres par date
- [ ] Mettre en place la limitation de débit (rate limiting)
- [ ] Documenter avec Swagger/OpenAPI

---

## 📚 Documentation détaillée

Pour des guides détaillés sur des endpoints spécifiques :

- **[Documentation Upload Image ESP32-CAM](./API_UPLOAD_IMAGE.md)** - Guide complet pour l'endpoint `/api/upload-image/`
  - Configuration ESP32-CAM
  - Exemples de code (Python, JavaScript, Arduino)
  - Détails techniques YOLO
  - Dépannage

---

**API Version** : 1.0  
**Dernière mise à jour** : 15 Janvier 2026
