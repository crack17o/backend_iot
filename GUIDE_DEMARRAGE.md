# 🚀 Guide de Démarrage Rapide - Système de Parking IoT

## 📋 Prérequis

- Python 3.8+
- SQLite (inclus avec Python)
- pip installé

---

## 1️⃣ Installation

### Étape 1: Cloner et installer les dépendances

```bash
# Activer l'environnement virtuel (si vous en avez un)
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 2: Migrations Django

```bash
cd parking
python manage.py makemigrations
python manage.py migrate
```

### Étape 4: Créer un superutilisateur

```bash
python manage.py createsuperuser
# Suivre les instructions pour créer un admin
```

---

## 2️⃣ Démarrer le Serveur

```bash
# Depuis le dossier parking/
python manage.py runserver
```

Le serveur sera accessible à `http://localhost:8000`

---

## 3️⃣ Première Utilisation

### Accès administration et utilisateurs

1. Aller sur `http://localhost:8000/admin`
2. Se connecter avec le superutilisateur créé
3. Créer des utilisateurs simples (nom, email, mot de passe) via l'admin si nécessaire

### Consulter le statut du parking

```bash
curl -X GET http://localhost:8000/api/parking/status/latest/
```

---

## 4️⃣ Configuration d'un Dispositif ESP32-CAM

### 4.1 Configurer l'ESP32-CAM

Dans votre code ESP32, envoyer les images avec une clé API simple définie dans `parking_monitor/utils/constants.py` (`ESP32_API_KEY`) :

```cpp
// Exemple Arduino/ESP32
#include <WiFi.h>
#include <HTTPClient.h>
#include <Camera.h>

const char* ssid = "VOTRE_WIFI";
const char* password = "VOTRE_PASSWORD";
const char* serverUrl = "http://votre-serveur:8000/api/parking/upload-image/";
const char* apiKey = "VOTRE_CLE_API"; // Même valeur que ESP32_API_KEY côté backend

void setup() {
  // Configuration WiFi et Camera
  // ...
}

void loop() {
  // Capturer une image
  camera_fb_t *fb = esp_camera_fb_get();
  
  if (fb) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("X-API-Key", apiKey);
    http.addHeader("Content-Type", "image/jpeg");
    
    int httpResponseCode = http.POST(fb->buf, fb->len);
    
    if (httpResponseCode == 201) {
      Serial.println("Image envoyée avec succès!");
    }
    
    http.end();
    esp_camera_fb_return(fb);
  }
  
  delay(10000); // Envoyer toutes les 10 secondes
}
```

---

## 5️⃣ Utilisation des Endpoints Principaux

### 5.1 Obtenir le statut actuel

```bash
curl -X GET http://localhost:8000/api/parking/status/latest/ \
  -H "Authorization: Bearer $TOKEN"
```

### 5.2 Consulter l'historique

```bash
# Tous les enregistrements
curl -X GET http://localhost:8000/api/parking/status/ \
  -H "Authorization: Bearer $TOKEN"

# Avec pagination
curl -X GET "http://localhost:8000/api/parking/status/?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"

# Filtrer par date
curl -X GET "http://localhost:8000/api/parking/status/?timestamp__gte=2024-01-01" \
  -H "Authorization: Bearer $TOKEN"
```

### 5.3 Statistiques (24h)

```bash
curl -X GET http://localhost:8000/api/parking/status/stats/ \
  -H "Authorization: Bearer $TOKEN"
```

### 5.4 Export CSV

```bash
curl -X GET "http://localhost:8000/api/parking/status/export-csv/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer $TOKEN" \
  -o rapport.csv
```

### 5.5 Export PDF

```bash
curl -X GET "http://localhost:8000/api/parking/status/export-pdf/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer $TOKEN" \
  -o rapport.pdf
```

### 5.6 Mise à jour manuelle (Admin uniquement)

```bash
curl -X POST http://localhost:8000/api/parking/update/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "occupied": 15,
    "total_spaces": 20
  }'
```

---

## 6️⃣ Gestion des Utilisateurs (Admin)

### 6.1 Créer un utilisateur admin

**Via l'interface Admin:**
1. Aller sur `http://localhost:8000/admin`
2. "Utilisateurs" → "Ajouter"
3. Remplir les informations
4. **Rôle**: Sélectionner "Administrateur"
5. Sauvegarder

### 6.2 Modifier le profil

```bash
curl -X PUT http://localhost:8000/api/parking/auth/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Nouveau",
    "last_name": "Nom",
    "phone": "+33123456789"
  }'
```

---

## 7️⃣ Test avec une Vidéo

Si vous avez une vidéo de test:

```bash
# Depuis la racine du projet
python counter.py videos/test.mp4
```

Le script analysera la vidéo et enverra les données toutes les 10 secondes.

---

## 8️⃣ Dépannage

### Erreur: "Module not found"
```bash
pip install -r requirements.txt
```

### Erreur: "Database connection failed"
- Vérifier que MySQL est en cours d'exécution
- Vérifier les credentials dans `parking/settings.py`
- Vérifier que la base `parking_db` existe

### Erreur: "Token expired"
```bash
# Rafraîchir le token
curl -X POST http://localhost:8000/api/parking/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<votre_refresh_token>"}'
```

### Erreur: "Permission denied"
- Vérifier que vous êtes connecté
- Vérifier votre rôle (certaines actions nécessitent `admin`)
- Vérifier que le token est valide

---

## 9️⃣ Structure des Réponses API

### Statut du Parking
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
  "device": 1,
  "device_name": "Caméra Parking Principal"
}
```

### Statistiques
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

## 🔐 Sécurité

- **Ne jamais commiter** les tokens API ou les credentials
- Utiliser HTTPS en production
- Changer `SECRET_KEY` en production
- Configurer `ALLOWED_HOSTS` en production
- Utiliser des mots de passe forts

---

**Bon développement ! 🚀**
