# Système de Parking IoT – Logique complète (environnement local)

Ce document décrit la **logique du système** de bout en bout : de la **prise d’image par l’ESP32-CAM** (module RHYX M21-45 / capteur GC2145) jusqu’à l’**affichage sur l’écran**, en passant par les **protocoles réseau** et la **sécurité** utilisés. Le déploiement décrit est encore **en local** (localhost / réseau local).

---

## 1. Vue d’ensemble

Le système repose sur :

- **ESP32-CAM** (module RHYX M21-45, capteur GC2145 2MP) : capture d’images du parking (JPEG) et envoi au serveur.
- **Backend Django** : réception des images, détection des véhicules (YOLO), enregistrement en base, exposition d’une API REST et d’une interface web.
- **Base SQLite** : stockage des statuts de parking et du trafic.
- **Interface web** : dashboard, historique parking, historique trafic, paramètres.

Toute la donnée de **parking** est considérée comme provenant de l’**ESP32-CAM** (y compris les mises à jour manuelles, enregistrées avec la même source pour cohérence).

---

## 2. Flux complet : de l’ESP32-CAM à l’écran

### 2.1 Prise d’image (ESP32-CAM RHYX M21-45)

- L’ESP32-CAM (module RHYX M21-45, capteur GC2145) capture une photo du parking (JPEG).
- Elle est prise à intervalle régulier (ex. toutes les 15 s, configurable dans le code Arduino).
- Résolution typique : 640×480 (VGA) ou plus, selon la config du sketch ; le backend redimensionne si besoin pour la détection.

### 2.2 Envoi vers le serveur (réseau local)

- **Protocole** : **HTTP/1.1**.
- **Méthode** : **POST**.
- **URL** : `http://<IP_SERVEUR>:8000/api/upload-image/`  
  Exemple en local : `http://localhost:8000/api/upload-image/`.
- **Content-Type** : **multipart/form-data** (upload de fichier).
- **Corps** : champ `image` contenant le fichier JPEG.
- **Authentification** : header **`X-API-Key: <clé_ESP32>`** (clé partagée configurée côté serveur dans `parking_monitor/utils/constants.py` → `ESP32_API_KEY`).

L’ESP32 envoie donc une requête du type :

```http
POST /api/upload-image/ HTTP/1.1
Host: <IP>:8000
X-API-Key: <votre_cle_esp32>
Content-Type: multipart/form-data; boundary=----...

------...
Content-Disposition: form-data; name="image"; filename="photo.jpg"
Content-Type: image/jpeg

<données binaires de l'image>
------...
```

### 2.3 Réception et sécurité côté serveur (Django)

1. **Vérification de la clé API**  
   Le backend lit `X-API-Key` (ou `api_key` en query). Si la valeur ne correspond pas à `ESP32_API_KEY`, il renvoie **401 Unauthorized**. Seuls les clients connaissant la clé (dont l’ESP32) peuvent uploader.

2. **Vérification du fichier**  
   - Présence du champ `image` dans la requête.  
   - Taille ≤ 10 Mo (`UPLOAD_MAX_SIZE` dans `constants.py`).  
   Sinon : **400 Bad Request**.

3. **Traitement**  
   Les octets de l’image sont lus en mémoire puis passés au module de détection.

### 2.4 Détection des véhicules (YOLO)

- **Module** : `parking_monitor/utils/car_detector.py` → classe `CarDetectorAPI`.
- **Modèle** : YOLOv10 (`yolov10n.pt`), classes COCO voiture / bus / camion (IDs 2, 5, 7).
- **Seuils** : confiance 0,25, IoU 0,45 (définis dans `constants.py`).
- **Étapes** :  
  - Décodage de l’image (bytes → tableau numpy).  
  - Redimensionnement si nécessaire (max 640×480).  
  - Inférence YOLO → boîtes englobantes des véhicules.  
  - Comptage des détections → **nombre de places occupées** (cap à 20 places, `PARKING_CAPACITY`).

Le résultat contient notamment : `count` (occupé), statut dérivé (disponible / plein), taux d’occupation.

### 2.5 Enregistrement en base de données

- **Modèle** : `ParkingStatus` (`parking_monitor/models.py`).
- **Champs renseignés** :  
  - `occupied` = résultat du comptage YOLO, plafonné à `total_spaces` (20).  
  - `total_spaces` = 20.  
  - `available`, `occupancy_rate`, `status` (available/full) : calculés dans la méthode `save()` du modèle.  
  - `image_path` : chemin de l’image stockée (ex. `uploads/esp32/2026/01/29/esp32_xxxxx.jpg`).  
  - **`source`** : toujours **`'esp32'`** (ESP32-CAM), y compris pour les mises à jour manuelles via l’API, afin que toute la donnée parking ait une source unique.
- **Stockage fichier** : l’image est enregistrée sur le disque (répertoire `uploads/esp32/...`) via le stockage Django (`default_storage`).
- **Base** : SQLite (`parking/db.sqlite3`).

### 2.6 Affichage sur l’écran

Les données sont consommées de deux manières :

- **API REST**  
  - **GET** `/api/status/` : liste paginée et filtrable des statuts.  
  - **GET** `/api/status/latest/` : dernier statut.  
  - **GET** `/api/status/stats/` : statistiques (ex. dernières 24 h).  
  - Authentification : **sessions Django** (cookie de session après connexion sur l’interface web) ou, selon la configuration, autre mécanisme d’API.

- **Interface web (templates Django)**  
  - **Dashboard** (`/`) : dernier parking, stats 24 h, dernier trafic, historiques récents.  
  - **Historique parking** (`/parking/`) : tableau filtré par date/heure, basé sur `ParkingStatus`.  
  - **Historique trafic** (`/traffic/`) : historique du trafic (Google Maps / trajet fixe).  
  - **Situation en direct** (`/live/`) : dernière situation parking + trafic.  
  - **Paramètres** (`/settings/`) : réglages (ex. activation/désactivation Google Maps).

Accès : **HTTP** vers `http://<IP>:8000/`, puis connexion avec un compte Django (admin/user). Les vues sont protégées par **@login_required** et, pour l’admin, **@user_passes_test(is_admin)**.

---

## 3. Schéma récapitulatif du flux parking

```
[ESP32-CAM]  --(1) capture image JPEG
      |
      v
[HTTP POST]   --(2) multipart/form-data + X-API-Key
      |
      v
[Django]      --(3) vérification clé API + taille fichier
      |
      v
[CarDetectorAPI] --(4) YOLO → comptage véhicules
      |
      v
[ParkingStatus]  --(5) sauvegarde BDD (source='esp32') + fichier image
      |
      v
[SQLite]      --(6) persistance
      |
      +---> [API REST]  --(7a) GET /api/status/... → clients (apps, scripts)
      |
      +---> [Templates] --(7b) Dashboard, Historique parking → navigateur
```

---

## 4. Protocoles réseau utilisés (local)

| Élément | Protocole / usage |
|--------|--------------------|
| Transport | **TCP** (HTTP). |
| Application | **HTTP/1.1** (GET pour la lecture, POST pour l’upload et les mises à jour). |
| Upload image | **POST** avec **multipart/form-data** (RFC 2388). |
| Authentification ESP32 | Header **X-API-Key** (clé partagée). |
| Authentification utilisateurs web | **Sessions Django** (cookie `sessionid`, stockage session côté serveur). |
| Données API | **JSON** pour les réponses (Content-Type: application/json). |
| Fichiers média | Servis en DEBUG par Django (`static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`). |

En local, l’accès se fait en **HTTP** ; pour un déploiement exposé, il faudrait **HTTPS** et éventuellement renforcer l’authentification (ex. tokens, reverse proxy).

---

## 5. Sécurité

| Mesure | Description |
|--------|-------------|
| **Clé API ESP32** | Une seule clé partagée (`ESP32_API_KEY`) ; à changer en production et à garder confidentielle. |
| **Validation des entrées** | Vérification de la présence et de la taille du fichier image ; serializers Django pour les champs API. |
| **Limite de taille** | 10 Mo max par image (`UPLOAD_MAX_SIZE`) pour limiter les abus et la charge. |
| **Accès aux vues web** | Connexion obligatoire (`@login_required`) ; certaines vues réservées aux admins (`is_admin`). |
| **Accès à l’API** | Endpoints protégés par authentification (sessions ou mécanisme configuré). |
| **Stockage des images** | Enregistrement dans `uploads/esp32/...` ; en production, servir les médias via un serveur dédié ou CDN, sans exposer de chemins sensibles. |

---

## 6. Fichiers clés (référence)

| Rôle | Fichier / répertoire |
|------|----------------------|
| Upload ESP32 + création `ParkingStatus` | `parking_monitor/views.py` → `upload_esp32_image` |
| Mise à jour manuelle (source = esp32) | `parking_monitor/views.py` → `update_parking_manual` |
| Détection YOLO | `parking_monitor/utils/car_detector.py` → `CarDetectorAPI` |
| Constantes (capacité, clé API, seuils) | `parking_monitor/utils/constants.py` |
| Modèle parking | `parking_monitor/models.py` → `ParkingStatus` |
| Routes API | `parking_monitor/urls.py` ; racine API : `parking/urls.py` → `api/` |
| Vues web (dashboard, historiques) | `parking_monitor/web_views.py` |
| Templates (écran) | `parking/templates/` (dashboard, parking_history, traffic_history, etc.) |
| Base de données | `parking/db.sqlite3` |

---

## 7. Trafic (complément)

Le **trafic** est géré à part : coordonnées fixes dans `constants.py`, appels optionnels à l’API Google Maps (Directions + trafic), enregistrement dans le modèle `TrafficStatus`. L’affichage trafic utilise les mêmes mécanismes (sessions, templates, API) que le reste de l’application. Ce README se concentre sur la **logique parking** et l’**ESP32-CAM (RHYX M21-45)** ; le code Arduino dédié est dans `README_ARDUINO_ESP32CAM.md`, le détail des endpoints trafic dans `API_DOCUMENTATION.md`.

---

**En résumé** : l’ESP32-CAM envoie une image en **HTTP POST** avec **X-API-Key** ; le serveur Django la traite avec **YOLO**, enregistre un **ParkingStatus** (toujours **source = ESP32-CAM**) et stocke l’image ; l’affichage sur l’écran passe par l’**API REST** et les **templates** web, avec **sessions Django** et contrôles d’accès pour la sécurité.
