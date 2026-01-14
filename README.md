# 🚗 Parking Intelligence - Système de Gestion de Parking avec IA

Un système intelligent de détection et de comptage de voitures garées utilisant YOLOv10 et Django, avec une API REST pour le suivi en temps réel de l'occupation du parking.

## 📋 Table des matières

- [Présentation](#présentation)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API](#api)
- [Endpoints](#endpoints)
- [Exemples](#exemples)

---

## 🎯 Présentation

**Parking Intelligence** est un système complet qui :

✅ Détecte et suit les véhicules garés en vidéo temps réel (YOLOv10)  
✅ Envoie les données d'occupation toutes les 10 secondes  
✅ Stocke l'historique dans une base de données MySQL  
✅ Fournit une API REST pour consulter l'état du parking  
✅ Indique si le parking est complet ou disponible  

---

## 🏗️ Architecture

```
backend_iot/
├── counter.py                  # Script de traitement vidéo
├── requirements.txt            # Dépendances Python
├── yolov10n.pt               # Modèle YOLO pré-entraîné
├── videos/                    # Dossier des vidéos
├── parking/                   # Projet Django
│   ├── manage.py
│   ├── db.sqlite3
│   ├── parking/              # Configuration Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── parking_monitor/      # Application de suivi
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── migrations/
└── README.md
```

### Composants

| Composant | Fonction |
|-----------|----------|
| **counter.py** | Analyse vidéo, détecte les voitures, envoie les données à l'API |
| **Django REST** | API pour consulter/mettre à jour l'état du parking |
| **MySQL** | Base de données pour l'historique |
| **YOLOv10n** | Modèle léger de détection d'objets (~50MB) |

---

## 💾 Installation

### Étape 1 : Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Étape 2 : Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 3 : Initialiser la base de données Django

```bash
cd parking
python manage.py migrate
cd ..
```

### Étape 4 : Créer un superutilisateur (optionnel)

```bash
cd parking
python manage.py createsuperuser
cd ..
```

---

## ⚙️ Configuration

### Configurer la capacité du parking

Éditer le fichier [counter.py](counter.py#L27) :

```python
PARKING_CAPACITY = 20  # Modifier selon votre parking
```

Et dans [parking_monitor/views.py](parking/parking_monitor/views.py#L9) :

```python
PARKING_CAPACITY = 20  # Doit être identique à counter.py
```

### Configurer la base de données MySQL (optionnel)

Par défaut, SQLite est utilisé. Pour MySQL, éditer [parking/settings.py](parking/parking/settings.py) :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'parking_db',
        'USER': 'root',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Paramètres de détection

Dans [counter.py](counter.py) :

```python
CONF_THRESHOLD = 0.4         # Confiance minimale (0-1)
STATIONARY_DISTANCE = 80     # Distance max en pixels (voiture immobile)
PARKING_TIME = 5             # Temps avant de compter comme stationnée (sec)
UPDATE_INTERVAL = 10         # Intervalle d'envoi API (sec)
```

---

## 🚀 Utilisation

### Démarrer le serveur Django

```bash
cd parking
python manage.py runserver
```

Le serveur est accessible à `http://localhost:8000`

### Analyser une vidéo

Dans un **autre terminal** (avec l'environnement venv activé) :

```bash
python counter.py videos/votre_video.mp4
```

**Exemple :**
```bash
python counter.py videos/test.mp4
```

### Consulter l'API

Voir les endpoints ci-dessous.

---

## 📡 API

### Base URL

```
http://localhost:8000/api
```

### Endpoints

#### 1️⃣ **Obtenir le statut actuel du parking**

```
GET /api/status/
```

**Réponse (200 OK) :**
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

---

#### 2️⃣ **Mettre à jour le statut du parking**

```
POST /api/status/update/
```

**Body (JSON) :**
```json
{
    "occupied": 5,
    "capacity": 20
}
```

**Réponse (201 Created) :**
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

---

#### 3️⃣ **Obtenir l'historique du parking**

```
GET /api/status/history/
```

**Réponse (200 OK) :**
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

## 📝 Exemples

### Exemple 1 : Analyser une vidéo

```bash
# Terminal 1 - Démarrer Django
cd parking
python manage.py runserver

# Terminal 2 - Analyser vidéo
python counter.py videos/test.mp4

# Output :
# [0s] Voitures stationnées: 0/20
# [API] ✓ Mise à jour envoyée - Occupés: 0/20 (0.0%) - Statut: available
# [5s] Voitures stationnées: 3/20
# [10s] Voitures stationnées: 5/20
# [API] ✓ Mise à jour envoyée - Occupés: 5/20 (25.0%) - Statut: available
```

### Exemple 2 : Consulter le statut via cURL

```bash
curl -X GET http://localhost:8000/api/status/
```

### Exemple 3 : Consulter l'historique

```bash
curl -X GET http://localhost:8000/api/status/history/
```

### Exemple 4 : Mettre à jour manuellement

```bash
curl -X POST http://localhost:8000/api/status/update/ \
  -H "Content-Type: application/json" \
  -d '{"occupied": 18, "capacity": 20}'
```

---

## 🔧 Dépannage

### ❌ Erreur : "Module not found"

```bash
pip install -r requirements.txt
```

### ❌ Erreur : "Cannot connect to API"

Assurez-vous que :
- Django est en cours d'exécution (`python manage.py runserver`)
- L'URL est correcte dans [counter.py](counter.py#L30)

### ❌ Erreur : "Video file not found"

Vérifiez que la vidéo existe dans le dossier `videos/` :

```bash
# Windows
dir videos/

# Linux/Mac
ls videos/
```

### ❌ Performance lente

- Réduire `FRAME_WIDTH` et `FRAME_HEIGHT` dans counter.py
- Utiliser une vidéo de résolution inférieure
- Augmenter `STATIONARY_DISTANCE` pour une détection moins sensible

---

## 📊 Schema de la Base de Données

### Table : parking_monitor_parkingstatus

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| timestamp | DATETIME | Horodatage de l'enregistrement |
| occupied | INTEGER | Nombre de places occupées |
| available | INTEGER | Nombre de places disponibles |
| status | VARCHAR | 'available' ou 'full' |
| occupancy_rate | FLOAT | Pourcentage d'occupation |

---

## 🔐 Sécurité (Production)

Avant de déployer en production :

1. **Modifier `settings.py`** :
   ```python
   DEBUG = False
   SECRET_KEY = "votre-clé-secrète-forte"
   ALLOWED_HOSTS = ["votredomaine.com"]
   ```

2. **Activer HTTPS**

3. **Sécuriser la base de données**

4. **Configurer CORS** si nécessaire

5. **Ajouter l'authentification API**

---

## 📄 Licence

MIT License

---

## 👨‍💻 Support

Pour toute question ou bug, consultez la documentation Django :
- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)

---

**Dernière mise à jour** : 14 Janvier 2026
