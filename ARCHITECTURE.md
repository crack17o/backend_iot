# 🏗️ Architecture du Système de Gestion de Parking IoT

## 📋 Vue d'ensemble

Système intelligent de gestion de parking basé sur l'IA (YOLOv10) et l'IoT (ESP32-CAM), avec API REST Django, sessions côté serveur, et export de rapports.

---

## 🎯 Objectifs

- ✅ Détection en temps réel de la disponibilité du parking (capacité: **20 véhicules**)
- ✅ Utilisation des sessions Django pour les utilisateurs (même serveur)
- ✅ Authentification simple des dispositifs ESP32-CAM via une clé API partagée
- ✅ Historique complet avec filtres par date
- ✅ Export de rapports (CSV/PDF)
- ✅ API REST complète et documentée

---

## 🏛️ Architecture Technique

### 1. **Modèles de Données**

#### `User` (Modèle personnalisé)
- Hérite de `AbstractUser`
- Rôles: `admin` ou `user`
- Champs: `username`, `email`, `role`, `phone`, `created_at`, `updated_at`

#### `ESP32Device`
- Gestion des dispositifs IoT authentifiés
- Champs: `device_id`, `device_name`, `api_token`, `is_active`, `created_by`, `last_seen`

#### `ParkingStatus`
- Enregistre l'état du parking à chaque instant
- Champs: `timestamp`, `occupied`, `total_spaces` (20), `available`, `status`, `occupancy_rate`, `source`, `device`, `image_path`

### 2. **Authentification**

#### JWT (JSON Web Tokens)
- **Access Token**: Durée de vie 1 heure
- **Refresh Token**: Durée de vie 7 jours
- Endpoints:
  - `POST /api/parking/auth/login/` - Connexion
  - `POST /api/parking/auth/refresh/` - Rafraîchir le token
  - `POST /api/parking/auth/register/` - Inscription
  - `GET/PUT /api/parking/auth/profile/` - Profil utilisateur

#### Authentification ESP32-CAM
- Token API unique par dispositif
- Header: `X-API-Token: <token>`
- Gestion via `/api/parking/devices/` (Admin uniquement)

### 3. **Permissions**

| Permission | Description | Accès |
|------------|-------------|-------|
| `IsAuthenticated` | Utilisateur connecté | Tous les endpoints |
| `IsAdminOrReadOnly` | Admin peut écrire, User peut lire | Mise à jour manuelle |
| `IsAdmin` | Administrateur uniquement | Gestion dispositifs, paramètres |
| `IsESP32Device` | Dispositif ESP32 authentifié | Upload d'images |

### 4. **API Endpoints**

#### Parking Status
- `GET /api/parking/status/` - Liste historique (paginée, filtrable)
- `GET /api/parking/status/latest/` - Dernier statut
- `GET /api/parking/status/stats/` - Statistiques 24h
- `GET /api/parking/status/export-csv/` - Export CSV
- `GET /api/parking/status/export-pdf/` - Export PDF
- `POST /api/parking/upload-image/` - Upload image ESP32 (token API ou JWT)
- `POST /api/parking/update/` - Mise à jour manuelle (Admin)

#### Authentification
- `POST /api/parking/auth/login/` - Connexion JWT
- `POST /api/parking/auth/refresh/` - Rafraîchir token
- `POST /api/parking/auth/register/` - Inscription
- `GET /api/parking/auth/profile/` - Profil utilisateur
- `PUT /api/parking/auth/profile/` - Mettre à jour profil

#### Gestion Dispositifs (Admin)
- `GET /api/parking/devices/` - Liste des dispositifs
- `POST /api/parking/devices/` - Créer un dispositif
- `GET /api/parking/devices/<id>/` - Détails d'un dispositif
- `PUT /api/parking/devices/<id>/` - Mettre à jour
- `DELETE /api/parking/devices/<id>/` - Supprimer

### 5. **Intelligence Artificielle**

#### YOLOv10
- Modèle: `yolov10n.pt` (léger, ~50MB)
- Classes détectées: Voitures (2), Bus (5), Camions (7)
- Seuil de confiance: 0.25
- Traitement: Images ESP32-CAM ou vidéos temps réel

#### Détection
- **Images**: Détection instantanée via `CarDetectorAPI`
- **Vidéos**: Tracking avec ByteTrack pour compter les véhicules stationnés

### 6. **Export de Rapports**

#### CSV
- Format: Colonnes séparées par virgule
- Filtres: `start_date`, `end_date`
- Colonnes: Date/Heure, Occupé, Disponible, Total, Taux (%), Statut, Source

#### PDF
- Généré avec ReportLab
- Contient: Statistiques globales, tableau des données, graphiques
- Limite: 100 enregistrements par PDF (pour performance)

---

## 🔐 Sécurité

### Authentification
- JWT avec rotation des tokens
- Tokens API uniques pour ESP32
- Validation des mots de passe (Django validators)

### Permissions
- Contrôle d'accès basé sur les rôles
- Endpoints sensibles réservés aux admins
- Historique en lecture seule pour tous

### Données
- Validation des entrées (serializers)
- Limite de taille des uploads (10MB)
- Indexation des champs fréquemment interrogés

---

## 📊 Base de Données

### Schéma Principal

```
User
├── id (PK)
├── username (unique)
├── email
├── role (admin/user)
└── ...

ESP32Device
├── id (PK)
├── device_id (unique)
├── api_token (unique)
├── is_active
├── created_by (FK → User)
└── ...

ParkingStatus
├── id (PK)
├── timestamp (indexed)
├── occupied
├── total_spaces (20)
├── available
├── status (available/full)
├── occupancy_rate
├── source (esp32/video/api)
├── device (FK → ESP32Device)
└── image_path
```

### Indexes
- `ParkingStatus.timestamp` (descendant)
- `ParkingStatus.status`
- `ParkingStatus.source`
- `User.role`
- `ESP32Device.api_token`

---

## 🚀 Déploiement

### Prérequis
- Python 3.8+
- MySQL 5.7+ (port 3307)
- Modèle YOLOv10 (`yolov10n.pt`)

### Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Migrations
cd parking
python manage.py makemigrations
python manage.py migrate

# 3. Créer un superutilisateur
python manage.py createsuperuser

# 4. Démarrer le serveur
python manage.py runserver
```

### Configuration ESP32-CAM

1. **Créer un dispositif** (via Admin ou API):
   ```bash
   POST /api/parking/devices/
   {
     "device_id": "ESP32_001",
     "device_name": "Caméra Parking Principal"
   }
   ```

2. **Récupérer le token API** depuis la réponse

3. **Configurer l'ESP32** pour envoyer les images avec le header:
   ```
   X-API-Token: <token_reçu>
   ```

---

## 📝 Exemples d'Utilisation

### 1. Connexion et récupération du statut

```bash
# Connexion
curl -X POST http://localhost:8000/api/parking/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# Récupérer le token depuis la réponse
TOKEN="<access_token>"

# Obtenir le statut actuel
curl -X GET http://localhost:8000/api/parking/status/latest/ \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Upload d'image depuis ESP32

```bash
curl -X POST http://localhost:8000/api/parking/upload-image/ \
  -H "X-API-Token: <token_esp32>" \
  -F "image=@photo.jpg"
```

### 3. Export CSV

```bash
curl -X GET "http://localhost:8000/api/parking/status/export-csv/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer $TOKEN" \
  -o rapport.csv
```

### 4. Créer un dispositif ESP32 (Admin)

```bash
curl -X POST http://localhost:8000/api/parking/devices/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_002",
    "device_name": "Caméra Parking Secondaire"
  }'
```

---

## 🔧 Configuration

### Capacité du Parking
- **Valeur fixe**: 20 véhicules
- Configurée dans: `parking_monitor/utils/constants.py`
- Utilisée dans: Modèles, Détecteur, API

### Paramètres YOLO
- `CONF_THRESHOLD`: 0.25
- `IOU_THRESHOLD`: 0.45
- `VEHICLE_CLASSES`: [2, 5, 7] (car, bus, truck)

### JWT
- Access Token: 1 heure
- Refresh Token: 7 jours
- Algorithme: HS256

---

## 📈 Évolutivité

### Scalabilité
- Pagination automatique (50 par page)
- Indexation des champs critiques
- Limite d'upload (10MB)
- Cache possible pour les statistiques

### Extensions possibles
- WebSocket pour temps réel
- Notifications push
- Multi-parkings
- Analyse prédictive
- Dashboard frontend (React/Vue)

---

## 🐛 Dépannage

### Erreur: "AUTH_USER_MODEL"
- Vérifier que `AUTH_USER_MODEL = 'parking_monitor.User'` dans `settings.py`
- Exécuter les migrations: `python manage.py migrate`

### Erreur: "Token invalide"
- Vérifier le format: `Authorization: Bearer <token>`
- Vérifier l'expiration du token
- Utiliser `/auth/refresh/` pour obtenir un nouveau token

### Erreur: "Permission denied"
- Vérifier le rôle de l'utilisateur
- Certaines actions nécessitent le rôle `admin`

---

**Dernière mise à jour**: Janvier 2026
