# 🚀 Démarrage rapide - Tester vos API

## Étape 1 : Démarrer le serveur Django

```bash
python manage.py runserver
```

Le serveur démarre sur `http://localhost:8000`

## Étape 2 : Choisir une méthode de test

### Option A : Interface navigateur (le plus simple) ⭐
Ouvrez dans votre navigateur :
- http://localhost:8000/api/status/latest/
- http://localhost:8000/api/status/stats/

Vous verrez une interface interactive pour tester les API !

### Option B : Script Python automatique
```bash
python test_api.py
```

Ce script teste automatiquement tous les endpoints.

### Option C : curl (ligne de commande)
```bash
# Dernier statut
curl http://localhost:8000/api/status/latest/

# Statistiques
curl http://localhost:8000/api/status/stats/

# Créer une entrée manuelle
curl -X POST http://localhost:8000/api/update/ ^
  -H "Content-Type: application/json" ^
  -d "{\"occupied\": 5, \"total_spaces\": 15}"
```

### Option D : Postman (collection complète prête) ⭐
1. **Importez la collection** :
   - Ouvrez Postman → "Import"
   - Sélectionnez `Parking_API.postman_collection.json`
   - **C'est prêt !** Toutes les requêtes sont configurées
   
2. **Démarrez le serveur** :
   ```bash
   python manage.py runserver
   ```

3. **Testez** :
   - Ouvrez la collection "Parking API"
   - Cliquez sur "GET - Dernier statut"
   - Cliquez sur "Send"

📖 Guide complet : `POSTMAN_SETUP.md`

---

## 📚 Documentation complète

Consultez **`API_TESTING_GUIDE.md`** pour :
- Tous les exemples détaillés
- Tous les endpoints disponibles
- Tests unitaires Django
- Gestion des erreurs
- Format des réponses

---

## 🔍 Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/status/latest/` | GET | Dernier statut |
| `/api/status/stats/` | GET | Statistiques 24h |
| `/api/status/` | GET | Historique (paginé) |
| `/api/update/` | POST | Mise à jour manuelle |
| `/api/upload-image/` | POST | Upload image ESP32 |

---

**Besoin d'aide ?** Consultez :
- `API_TESTING_GUIDE.md` - Guide complet de test
- `API_UPLOAD_IMAGE.md` - Documentation détaillée pour l'upload d'image
