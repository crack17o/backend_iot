# 📤 Documentation API - Upload Image ESP32-CAM

## 📋 Vue d'ensemble

L'endpoint `upload_esp32_image` permet d'uploader une image depuis un ESP32-CAM et d'effectuer une détection automatique des véhicules en utilisant le modèle YOLOv10. L'API analyse l'image, compte les voitures détectées et enregistre les résultats dans la base de données.

### Fonctionnalités principales

- ✅ Upload d'image JPEG depuis ESP32-CAM
- ✅ Détection automatique des véhicules avec YOLOv10
- ✅ Comptage des voitures, bus et camions
- ✅ Calcul automatique des places disponibles
- ✅ Sauvegarde de l'image avec organisation par date
- ✅ Enregistrement des résultats en base de données
- ✅ Validation de la taille du fichier (max 10MB)

---

## 🔗 Endpoint

### URL
```
POST /api/upload-image/
```

### Méthode
**POST**

### Base URL
```
http://localhost:8000/api/upload-image/
```

En production, remplacez `localhost:8000` par l'adresse de votre serveur.

---

## 📥 Requête

### Headers
Aucun header spécial n'est requis. Le content-type est automatiquement géré par le format `multipart/form-data`.

### Body (Form-data)

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `image` | File | ✅ **Oui** | Fichier image JPEG/JPG |
| `source` | String | ❌ Non | Source de l'image (par défaut: `esp32`) |

#### Détails des champs

**`image` (File)**
- **Format accepté** : JPEG, JPG
- **Taille maximale** : 10 MB (10 485 760 octets)
- **Recommandation** : Résolution 640x480 (optimale pour ESP32-CAM)

**`source` (String, optionnel)**
- Valeurs possibles : `esp32`, `video`, `api`
- Par défaut : `esp32` si non spécifié
- Utilisé pour tracer l'origine de la donnée

### Exemple de requête

#### Avec cURL
```bash
curl -X POST http://localhost:8000/api/upload-image/ \
  -F "image=@/chemin/vers/image.jpg" \
  -F "source=esp32"
```

#### Avec Python requests
```python
import requests

url = "http://localhost:8000/api/upload-image/"

with open("image.jpg", "rb") as image_file:
    files = {"image": ("image.jpg", image_file, "image/jpeg")}
    data = {"source": "esp32"}  # Optionnel
    
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

#### Avec JavaScript (Fetch)
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]); // fileInput est un <input type="file">
formData.append('source', 'esp32'); // Optionnel

fetch('http://localhost:8000/api/upload-image/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

#### Avec Postman
1. Méthode : **POST**
2. URL : `http://localhost:8000/api/upload-image/`
3. Body → form-data
4. Ajouter :
   - Key: `image` (Type: **File**)
   - Value: Sélectionner un fichier image
   - Key: `source` (Type: **Text**, optionnel)
   - Value: `esp32`

#### Code ESP32-CAM (Arduino)
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_camera.h>

const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_MOT_DE_PASSE";
const char* serverURL = "http://VOTRE_SERVEUR:8000/api/upload-image/";

void setup() {
    Serial.begin(115200);
    
    // Configuration WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connexion WiFi...");
    }
    Serial.println("WiFi connecté!");
    
    // Configuration caméra
    camera_config_t config;
    config.pin_pwdn = -1;
    config.pin_reset = -1;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 12;
    config.fb_count = 1;
    
    esp_camera_init(&config);
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        // Capturer une image
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Échec capture");
            return;
        }
        
        // Envoyer l'image
        HTTPClient http;
        http.begin(serverURL);
        http.addHeader("Content-Type", "multipart/form-data");
        
        String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
        http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
        
        String body = "--" + boundary + "\r\n";
        body += "Content-Disposition: form-data; name=\"image\"; filename=\"image.jpg\"\r\n";
        body += "Content-Type: image/jpeg\r\n\r\n";
        
        http.POST((uint8_t*)fb->buf, fb->len);
        
        int httpResponseCode = http.POST(body + String((char*)fb->buf, fb->len) + "\r\n--" + boundary + "--\r\n");
        
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("Réponse: " + response);
        } else {
            Serial.println("Erreur: " + String(httpResponseCode));
        }
        
        http.end();
        esp_camera_fb_return(fb);
    }
    
    delay(30000); // Attendre 30 secondes avant la prochaine capture
}
```

---

## 📤 Réponse

### Succès (201 Created)

Lorsque l'upload et la détection réussissent, l'API retourne un objet JSON avec les détails du statut du parking.

#### Structure de la réponse

```json
{
    "id": 42,
    "timestamp": "2026-01-15T14:30:45.123456Z",
    "occupied": 5,
    "total_spaces": 15,
    "available": 10,
    "status": "available",
    "occupancy_rate": 33.3,
    "image_path": "uploads/esp32/2026/01/15/esp32_a526be4e.jpg",
    "source": "esp32",
    "detected_count": 5
}
```

#### Description des champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | ID unique de l'enregistrement dans la base de données |
| `timestamp` | DateTime (ISO 8601) | Date et heure de l'enregistrement (UTC) |
| `occupied` | Integer | Nombre de véhicules détectés (places occupées) |
| `total_spaces` | Integer | Capacité totale du parking (15 par défaut) |
| `available` | Integer | Nombre de places disponibles (calculé automatiquement) |
| `status` | String | Statut du parking : `"available"` ou `"full"` |
| `occupancy_rate` | Float | Taux d'occupation en pourcentage (0.0 à 100.0) |
| `image_path` | String | Chemin relatif où l'image a été sauvegardée |
| `source` | String | Source de l'image (`esp32`, `video`, ou `api`) |
| `detected_count` | Integer | Nombre de véhicules détectés (identique à `occupied`) |

### Erreurs

#### 400 Bad Request - Aucune image fournie

```json
{
    "error": "Aucune image fournie"
}
```

**Cause** : Le champ `image` est manquant dans la requête.

**Solution** : Vérifiez que vous envoyez bien un fichier dans le champ `image`.

---

#### 400 Bad Request - Fichier trop volumineux

```json
{
    "error": "Fichier trop volumineux (max 10MB)"
}
```

**Cause** : La taille du fichier dépasse 10 MB.

**Solution** : Réduisez la résolution ou la qualité JPEG de l'image.

**Recommandations pour ESP32-CAM** :
- Résolution : 640x480 (VGA) ou 800x600 (SVGA)
- Qualité JPEG : 10-15 (compromis qualité/taille)
- Taille attendue : ~50-200 KB

---

#### 400 Bad Request - Erreur de détection

```json
{
    "error": "Impossible de décoder l'image"
}
```

ou

```json
{
    "error": "Format d'image non supporté"
}
```

**Causes possibles** :
- Format d'image non supporté (seul JPEG/JPG est accepté)
- Fichier corrompu
- Données d'image invalides

**Solution** : Vérifiez que l'image est bien au format JPEG valide.

---

#### 500 Internal Server Error

```json
{
    "error": "Erreur détaillée du serveur"
}
```

**Causes possibles** :
- Erreur lors du chargement du modèle YOLO
- Problème d'accès au stockage de fichiers
- Erreur de connexion à la base de données
- Autre erreur serveur

**Solution** : Vérifiez les logs du serveur Django pour plus de détails.

---

## ⚙️ Processus de traitement

L'endpoint `upload_esp32_image` suit ce processus étape par étape :

### 1. Validation de la requête
- ✅ Vérifie la présence du champ `image`
- ✅ Vérifie la taille du fichier (max 10 MB)
- ✅ Lit les données binaires de l'image

### 2. Initialisation du détecteur
- ✅ Crée une instance de `CarDetectorAPI`
- ✅ Charge le modèle YOLOv10 (ou le télécharge si absent)
- ✅ Configure les paramètres de détection :
  - Classes de véhicules : voitures (2), bus (5), camions (7)
  - Seuil de confiance : 0.25 (25%)
  - Seuil IoU : 0.45

### 3. Traitement de l'image
- ✅ Décodage de l'image depuis les bytes
- ✅ Redimensionnement automatique si nécessaire (>640x480)
- ✅ Détection des véhicules avec YOLOv10
- ✅ Comptage des véhicules détectés

### 4. Calcul des métriques
- ✅ Calcul du nombre de places occupées
- ✅ Calcul du nombre de places disponibles
- ✅ Calcul du taux d'occupation (%)
- ✅ Détermination du statut (available/full)

### 5. Sauvegarde
- ✅ Sauvegarde de l'image dans `uploads/esp32/YYYY/MM/DD/`
- ✅ Nom de fichier : `esp32_{UUID_8_chars}.jpg`
- ✅ Création d'un enregistrement dans la base de données

### 6. Réponse
- ✅ Retour des données au format JSON
- ✅ Code HTTP 201 (Created)

---

## 🔍 Détails techniques

### Modèle de détection : YOLOv10

Le système utilise **YOLOv10** (You Only Look Once version 10) pour la détection d'objets.

#### Classes détectées

| ID COCO | Classe | Description |
|---------|--------|-------------|
| 2 | Car | Voiture de tourisme |
| 5 | Bus | Autobus |
| 7 | Truck | Camion |

**Note** : Seuls les véhicules (voitures, bus, camions) sont comptés. Les vélos, motos et autres véhicules ne sont pas inclus.

#### Paramètres de détection

- **Seuil de confiance** : 0.25 (25%)
  - Un véhicule doit avoir au moins 25% de confiance pour être détecté
  - Plus bas = plus sensible mais peut générer des faux positifs
  
- **Seuil IoU** : 0.45
  - Utilisé pour la suppression non-maximale (NMS)
  - Évite les doublons de détection pour le même objet

#### Performance

- **Résolution optimale** : 640x480 pixels
- **Temps de traitement** : ~200-500ms par image (CPU)
- **Précision** : ~90-95% selon les conditions d'éclairage

### Stockage des images

Les images sont organisées par date dans la structure suivante :

```
uploads/
└── esp32/
    └── YYYY/
        └── MM/
            └── DD/
                ├── esp32_a526be4e.jpg
                ├── esp32_b3f4c5d6.jpg
                └── ...
```

**Avantages** :
- Organisation chronologique
- Facilite les sauvegardes
- Performance optimale pour l'accès

### Base de données

Chaque upload crée un nouvel enregistrement dans la table `parking_status` avec :
- Les métriques calculées (occupied, available, occupancy_rate)
- Le chemin de l'image
- La source (`esp32`)
- Le timestamp

---

## 📊 Exemples de réponses

### Exemple 1 : Parking avec places disponibles

```json
{
    "id": 42,
    "timestamp": "2026-01-15T14:30:45.123456Z",
    "occupied": 5,
    "total_spaces": 15,
    "available": 10,
    "status": "available",
    "occupancy_rate": 33.3,
    "image_path": "uploads/esp32/2026/01/15/esp32_a526be4e.jpg",
    "source": "esp32",
    "detected_count": 5
}
```

**Interprétation** : 5 véhicules détectés sur 15 places. 10 places disponibles (66.7% de disponibilité).

---

### Exemple 2 : Parking complet

```json
{
    "id": 43,
    "timestamp": "2026-01-15T15:00:12.456789Z",
    "occupied": 15,
    "total_spaces": 15,
    "available": 0,
    "status": "full",
    "occupancy_rate": 100.0,
    "image_path": "uploads/esp32/2026/01/15/esp32_b3f4c5d6.jpg",
    "source": "esp32",
    "detected_count": 15
}
```

**Interprétation** : Parking complet, toutes les places sont occupées (100%).

---

### Exemple 3 : Parking vide

```json
{
    "id": 44,
    "timestamp": "2026-01-15T16:15:30.789012Z",
    "occupied": 0,
    "total_spaces": 15,
    "available": 15,
    "status": "available",
    "occupancy_rate": 0.0,
    "image_path": "uploads/esp32/2026/01/15/esp32_c7d8e9f0.jpg",
    "source": "esp32",
    "detected_count": 0
}
```

**Interprétation** : Aucun véhicule détecté. 15 places disponibles (100%).

---

## 🎯 Cas d'usage

### 1. ESP32-CAM - Envoi périodique

L'ESP32-CAM capture et envoie une image toutes les 30 secondes :

```cpp
void loop() {
    // ... capture image ...
    // ... envoi HTTP POST ...
    delay(30000); // 30 secondes
}
```

### 2. Application mobile

Une application mobile peut uploader une image pour vérifier le parking :

```javascript
// Après avoir pris une photo
const formData = new FormData();
formData.append('image', photoFile);

const response = await fetch('https://api.example.com/api/upload-image/', {
    method: 'POST',
    body: formData
});

const data = await response.json();
console.log(`Parking: ${data.available}/${data.total_spaces} places disponibles`);
```

### 3. Intégration web

Un dashboard web peut envoyer des images manuellement :

```html
<input type="file" id="imageInput" accept="image/jpeg">
<button onclick="uploadImage()">Vérifier le parking</button>

<script>
async function uploadImage() {
    const file = document.getElementById('imageInput').files[0];
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await fetch('/api/upload-image/', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    alert(`${data.available} places disponibles`);
}
</script>
```

---

## ⚡ Optimisation et performances

### Recommandations pour ESP32-CAM

1. **Résolution** : Utilisez VGA (640x480) pour un bon compromis
2. **Qualité JPEG** : 10-15 pour réduire la taille (~100-200 KB)
3. **Fréquence** : Envoyez toutes les 30-60 secondes (pas plus souvent)
4. **WiFi** : Utilisez une connexion stable

### Limites

- **Taille max** : 10 MB par fichier
- **Format** : JPEG/JPG uniquement
- **Temps de traitement** : ~200-500ms (selon le serveur)
- **Débit** : Gérez la fréquence d'envoi pour éviter la surcharge

---

## 🔧 Configuration

### Modifier la capacité du parking

Éditez `parking/parking_monitor/utils/constants.py` :

```python
PARKING_CAPACITY = 15  # Changez cette valeur
```

### Modifier la taille maximale

Éditez `parking/parking_monitor/utils/constants.py` :

```python
UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
```

### Modifier les paramètres YOLO

Éditez `parking/parking_monitor/utils/car_detector.py` dans `__init__` :

```python
self.conf_threshold = 0.25  # Seuil de confiance (0.0 à 1.0)
self.iou_threshold = 0.45   # Seuil IoU (0.0 à 1.0)
```

---

## 🐛 Dépannage

### Problème : "Aucune image fournie"

**Solutions** :
- Vérifiez que le champ s'appelle bien `image` (pas `file`, `photo`, etc.)
- Assurez-vous d'utiliser `multipart/form-data`
- Vérifiez que le fichier est bien attaché à la requête

### Problème : Erreur 500 - Modèle YOLO

**Solutions** :
- Vérifiez que `yolov10n.pt` est accessible
- Le modèle sera téléchargé automatiquement si absent
- Vérifiez l'espace disque (le modèle fait ~5.5 MB)

### Problème : Aucun véhicule détecté alors qu'il y en a

**Solutions** :
- Réduisez le `conf_threshold` (par exemple à 0.20)
- Améliorez l'éclairage de la scène
- Vérifiez la résolution et la qualité de l'image
- Les véhicules trop petits ou trop loin peuvent ne pas être détectés

### Problème : Faux positifs (véhicules détectés alors qu'il n'y en a pas)

**Solutions** :
- Augmentez le `conf_threshold` (par exemple à 0.30)
- Améliorez la qualité de l'image
- Vérifiez l'angle de la caméra

---

## 📚 Ressources complémentaires

- [Guide de test des API](./API_TESTING_GUIDE.md)
- [Documentation Postman](./POSTMAN_SETUP.md)
- [Documentation générale de l'API](./API_DOCUMENTATION.md)
- [Ultralytics YOLO Documentation](https://docs.ultralytics.com/)

---

**Dernière mise à jour** : 15 Janvier 2026
