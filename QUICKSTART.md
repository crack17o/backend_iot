# 🚀 Guide de Démarrage Rapide

## Installation (Windows)

### 1️⃣ Ouvrir PowerShell dans le dossier du projet

```powershell
cd C:\Users\USER\Downloads\backend_iot
```

### 2️⃣ Créer l'environnement virtuel

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3️⃣ Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 4️⃣ Initialiser la base de données

```powershell
cd parking
python manage.py migrate
cd ..
```

---

## Lancer le projet

### Terminal 1 - Démarrer le serveur Django

```powershell
cd parking
python manage.py runserver
```

✅ Le serveur est disponible à `http://localhost:8000`

### Terminal 2 - Analyser une vidéo

```powershell
python counter.py videos/test.mp4
```

---

## Tester l'API

### Ouvrir un navigateur

```
http://localhost:8000/api/status/
```

### Ou utiliser cURL

```powershell
# Obtenir le statut actuel
curl -X GET http://localhost:8000/api/status/

# Obtenir l'historique
curl -X GET http://localhost:8000/api/status/history/

# Mettre à jour manuellement
curl -X POST http://localhost:8000/api/status/update/ `
  -H "Content-Type: application/json" `
  -d '{\"occupied\": 5, \"capacity\": 20}'
```

---

## Structure des réponses API

### GET /api/status/ 
```json
{
    "occupied": 5,
    "available": 15,
    "capacity": 20,
    "occupancy_rate": "25.0%",
    "status": "available",
    "is_full": false,
    "timestamp": "2024-01-14T10:30:45Z"
}
```

### POST /api/status/update/
```json
{
    "success": true,
    "occupied": 5,
    "available": 15,
    "capacity": 20,
    "occupancy_rate": "25.0%",
    "status": "available"
}
```

---

## Fichiers clés à modifier

### Capacité du parking
- **counter.py** ligne 27 : `PARKING_CAPACITY = 20`
- **parking/parking_monitor/views.py** ligne 9 : `PARKING_CAPACITY = 20`

### Paramètres de détection
- **counter.py** lignes 19-25

### Configuration Django
- **parking/parking/settings.py**

---

## Commandes utiles

```powershell
# Voir tous les enregistrements de statut
cd parking
python manage.py shell
# Puis dans le shell Python :
# from parking_monitor.models import ParkingStatus
# ParkingStatus.objects.all()

# Créer un superutilisateur pour l'admin
python manage.py createsuperuser

# Réinitialiser la base de données
python manage.py flush  # ⚠️ Supprime toutes les données
```

---

## Troubleshooting

| Problème | Solution |
|----------|----------|
| ModuleNotFoundError | Exécuter `pip install -r requirements.txt` |
| API non accessible | Vérifier que Django est en cours d'exécution |
| Vidéo non trouvée | Vérifier le chemin de la vidéo dans `videos/` |
| Database error | Exécuter `python manage.py migrate` |

---

**Enjoy! 🎉**
