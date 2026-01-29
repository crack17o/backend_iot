# 🚀 Guide de Démarrage Rapide - Parking Intelligence

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Clé API Google Maps (pour la fonctionnalité de trafic)

---

## ⚡ Installation Rapide

### 1. Accéder au dossier racine du projet

```bash
# Vous devez être dans le dossier backend_iot (racine du projet)
# Le fichier requirements.txt doit être visible
```

### 2. Créer un environnement virtuel (recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**Note :** L'environnement virtuel peut être créé à la racine ou dans le dossier `parking/`.

### 3. Installer les dépendances

```bash
# Depuis la racine du projet (où se trouve requirements.txt)
pip install -r requirements.txt
```

### 4. Se placer dans le dossier du projet Django

```bash
cd parking
```

### 5. Créer la base de données (SQLite)

```bash
python manage.py migrate
```

**⚠️ IMPORTANT :** Cette étape doit être faite **avant** de créer les administrateurs.

Cette commande :
- Crée le fichier `db.sqlite3` dans le dossier `parking/` (base de données SQLite)
- Crée toutes les tables nécessaires (ParkingStatus, TrafficStatus, User, etc.)
- Initialise la structure de la base de données

### 6. Créer les administrateurs

```bash
python manage.py create_admins
```

**⚠️ IMPORTANT :** Cette commande doit être exécutée **après** la création de la base de données (étape 5).

Cette commande crée automatiquement les 12 administrateurs suivants :
- **Jael, Stone, Jelly, Nehemy, Nehemie, Eddy, Elyel, Josephat, Ruth, Ernick, Enoch, Jonathan**

**Mot de passe pour tous :** `1234567890`

Cette commande crée automatiquement les 12 administrateurs suivants :
- **Jael, Stone, Jelly, Nehemy, Nehemie, Eddy, Elyel, Josephat, Ruth, Ernick, Enoch, Jonathan**

**Mot de passe pour tous :** `1234567890`

### 7. Créer un superutilisateur Django (optionnel)

```bash
python manage.py createsuperuser
```

**Note :** Cette étape est optionnelle car les administrateurs sont déjà créés avec `create_admins` (étape 6).

---

## ⚙️ Configuration

### 1. Configurer les coordonnées GPS

Les coordonnées GPS peuvent être modifiées de deux façons :

#### Option A : Via l'interface web (recommandé)
1. Se connecter au dashboard : `http://localhost:8000/`
2. Cliquer sur "Paramètres" dans le menu
3. Modifier les coordonnées du point de départ et d'arrivée
4. Cliquer sur "Enregistrer les modifications"

#### Option B : Via le fichier `constants.py`
Éditer `parking/parking_monitor/utils/constants.py` :

```python
# Coordonnées GPS fixes pour le trajet (aller/retour)
ROUTE_START_LATITUDE = 48.8566   # Latitude point de départ
ROUTE_START_LONGITUDE = 2.3522   # Longitude point de départ
ROUTE_END_LATITUDE = 48.8606     # Latitude point d'arrivée
ROUTE_END_LONGITUDE = 2.3376     # Longitude point d'arrivée
```

### 2. Configurer la clé API Google Maps

Éditer `parking/parking_monitor/utils/constants.py` :

```python
GOOGLE_MAPS_API_KEY = "VOTRE_CLE_API_GOOGLE_MAPS"
```

**Comment obtenir une clé API Google Maps :**
1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un projet ou sélectionner un projet existant
3. Activer l'API "Directions API"
4. Créer une clé API dans "Identifiants"
5. Copier la clé dans le fichier `constants.py`

### 3. Configurer la clé API ESP32 (optionnel)

Éditer `parking/parking_monitor/utils/constants.py` :

```python
ESP32_API_KEY = "VOTRE_CLE_ESP32_SECURISEE"
```

---

## 🏃 Démarrer le serveur

```bash
python manage.py runserver
```

Le serveur démarre sur : `http://localhost:8000/`

---

## 🌐 Accès à l'interface

### Dashboard Web
- **URL :** `http://localhost:8000/`
- **Authentification :** Utiliser un des admins créés avec `create_admins`
- **Fonctionnalités :**
  - Vue d'ensemble du parking (statut actuel, statistiques)
  - Vue d'ensemble du trafic (aller/retour)
  - Historique du parking avec filtres
  - Historique du trafic avec filtres
  - Paramètres (modification des coordonnées GPS)

### Interface Admin Django
- **URL :** `http://localhost:8000/admin/`
- **Authentification :** Utiliser un des admins créés

---

## 📡 API Endpoints

### Parking

- `GET /api/parking/status/` - Liste historique (paginée)
- `GET /api/parking/status/latest/` - Dernier statut
- `GET /api/parking/status/stats/` - Statistiques 24h
- `GET /api/parking/status/export-csv/` - Export CSV
- `GET /api/parking/status/export-pdf/` - Export PDF
- `POST /api/parking/upload-image/` - Upload image ESP32-CAM
- `POST /api/parking/update/` - Mise à jour manuelle

### Trafic

- `GET /api/traffic/status/` - Historique complet
- `GET /api/traffic/status/latest/` - Dernier statut par direction
- `GET /api/traffic/status/direction/<direction>/` - Historique par direction
- `POST /api/traffic/check/` - Vérifier le trafic en temps réel

**Exemple de vérification du trafic :**
```bash
curl -X POST http://localhost:8000/api/traffic/check/ \
  -H "Content-Type: application/json" \
  -d '{"direction": "aller"}'
```

---

## 🔧 Commandes utiles

### Créer les administrateurs
```bash
python manage.py create_admins
```

### Créer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### Accéder au shell Django
```bash
python manage.py shell
```

### Collecter les fichiers statiques (production)
```bash
python manage.py collectstatic
```

---

## 🧪 Test rapide

### 1. Tester l'API Parking

```bash
# Obtenir le dernier statut
curl http://localhost:8000/api/parking/status/latest/

# Mettre à jour manuellement
curl -X POST http://localhost:8000/api/parking/update/ \
  -H "Content-Type: application/json" \
  -d '{"occupied": 5, "total_spaces": 20}'
```

### 2. Tester l'API Trafic

```bash
# Vérifier le trafic aller
curl -X POST http://localhost:8000/api/traffic/check/ \
  -H "Content-Type: application/json" \
  -d '{"direction": "aller"}'

# Obtenir le dernier statut
curl http://localhost:8000/api/traffic/status/latest/
```

### 3. Tester l'interface web

1. Ouvrir `http://localhost:8000/`
2. Se connecter avec un admin (ex: `Jael` / `1234567890`)
3. Vérifier le dashboard
4. Tester la vérification du trafic depuis l'interface
5. Modifier les coordonnées GPS dans "Paramètres"

---

## 📝 Structure du projet

```
parking/
├── parking_monitor/          # Application principale
│   ├── models.py            # Modèles de données
│   ├── views.py             # Vues API
│   ├── web_views.py         # Vues web (dashboard)
│   ├── serializers.py       # Sérialiseurs DRF
│   ├── urls.py              # URLs API
│   ├── web_urls.py          # URLs web
│   ├── admin.py             # Configuration admin Django
│   ├── utils/               # Utilitaires
│   │   ├── car_detector.py  # Détection YOLO
│   │   ├── google_maps.py   # API Google Maps
│   │   ├── constants.py     # Constantes (GPS, clés API)
│   │   └── reports.py       # Génération de rapports
│   └── management/
│       └── commands/
│           └── create_admins.py  # Script création admins
├── templates/               # Templates HTML
│   ├── base.html           # Layout principal
│   ├── dashboard.html      # Dashboard
│   ├── parking_history.html # Historique parking
│   ├── traffic_history.html # Historique trafic
│   └── settings.html       # Paramètres GPS
├── settings.py             # Configuration Django
└── requirements.txt         # Dépendances Python
```

---

## 🐛 Dépannage

### Erreur : "Clé API Google Maps non configurée"
- Vérifier que `GOOGLE_MAPS_API_KEY` est configurée dans `constants.py`
- Vérifier que la clé API est valide et que l'API Directions est activée

### Erreur : "Module not found"
- Vérifier que l'environnement virtuel est activé
- Réinstaller les dépendances : `pip install -r requirements.txt`

### Erreur : "No module named 'django'"
- Installer Django : `pip install django`
- Ou réinstaller toutes les dépendances : `pip install -r requirements.txt`

### Erreur : "Database does not exist" ou "no such table"
- **Solution :** Créer la base de données avec les migrations
  ```bash
  cd parking
  python manage.py migrate
  ```
  Cette commande crée automatiquement le fichier `db.sqlite3` et toutes les tables nécessaires.
  **⚠️ À faire avant de créer les administrateurs ou d'utiliser l'application.**

### Erreur : "Could not open requirements file"
- **Solution :** Vérifiez que vous êtes dans le bon dossier
  - Le fichier `requirements.txt` est à la **racine** du projet (`backend_iot/`)
  - Si vous êtes dans `parking/`, remontez d'un niveau : `cd ..`
  - Puis installez : `pip install -r requirements.txt`

### Erreur : "Permission denied" sur l'interface web
- Vérifier que l'utilisateur est connecté et est admin (`is_staff=True`)
- Créer les admins : `python manage.py create_admins`
- **⚠️ Important :** Créer d'abord la base de données avec `python manage.py migrate` avant de créer les admins

### Les coordonnées GPS ne se mettent pas à jour
- Vérifier les permissions d'écriture sur `constants.py`
- Redémarrer le serveur Django après modification
- Vérifier que les valeurs sont valides (latitudes: -90 à 90, longitudes: -180 à 180)

---

## 📚 Documentation complète

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Architecture détaillée du système
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Documentation complète de l'API
- **[GUIDE_DEMARRAGE.md](./GUIDE_DEMARRAGE.md)** - Guide détaillé de démarrage

---

## ✅ Checklist de démarrage

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] **Base de données créée** (`cd parking` puis `python manage.py migrate`)
- [ ] Admins créés (`python manage.py create_admins`)
- [ ] Coordonnées GPS configurées (via interface ou `constants.py`)
- [ ] Clé API Google Maps configurée (si utilisation du trafic)
- [ ] Serveur démarré (`python manage.py runserver`)
- [ ] Interface web accessible (`http://localhost:8000/`)
- [ ] Connexion testée avec un admin

---

## 🎯 Prochaines étapes

1. **Configurer l'ESP32-CAM** : Connecter votre dispositif ESP32-CAM pour l'envoi automatique d'images
2. **Configurer les coordonnées GPS** : Définir les points de départ et d'arrivée pour le suivi du trafic
3. **Personnaliser** : Ajuster les paramètres selon vos besoins (capacité parking, seuils de trafic, etc.)
4. **Surveiller** : Utiliser le dashboard pour surveiller l'état du parking et du trafic en temps réel

---

**Version :** 2.0  
**Dernière mise à jour :** Janvier 2026
