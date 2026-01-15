# 🚀 Guide Postman - Système de Parking

## Installation rapide

### Étape 1 : Importer la collection

1. **Ouvrez Postman**
2. **Cliquez sur "Import"** (bouton en haut à gauche)
3. **Glissez-déposez** ou **sélectionnez** le fichier :
   ```
   Parking_API.postman_collection.json
   ```
4. **Cliquez sur "Import"**

✅ La collection "Parking API - Système de Surveillance" est maintenant disponible !

### Étape 2 : Configurer l'environnement (optionnel mais recommandé)

#### Option A : Utiliser les variables de collection (simple)
- La collection a déjà la variable `base_url` configurée
- Par défaut : `http://localhost:8000/api`
- Vous pouvez la modifier dans la collection si besoin

#### Option B : Créer un environnement (avancé)

1. **Créer un nouvel environnement** :
   - Cliquez sur l'icône ⚙️ (engrenage) en haut à droite
   - Cliquez sur "Add"
   - Nommez-le "Parking Local"

2. **Ajouter des variables** :
   | Variable | Valeur initiale | Valeur actuelle |
   |----------|----------------|-----------------|
   | `base_url` | `http://localhost:8000/api` | `http://localhost:8000/api` |

3. **Sélectionner l'environnement** :
   - Dans le menu déroulant en haut à droite, sélectionnez "Parking Local"

4. **Pour la production** :
   - Créez un environnement "Parking Production"
   - Mettez `base_url` à votre URL de production

### Étape 3 : Démarrer le serveur Django

```bash
cd parking
python manage.py runserver
```

Le serveur démarre sur `http://localhost:8000`

### Étape 4 : Tester !

1. **Ouvrez la collection** dans Postman
2. **Cliquez sur "GET - Dernier statut"**
3. **Cliquez sur "Send"** (Bouton bleu en haut à droite)
4. **Vérifiez la réponse** dans le panneau du bas

## 📋 Structure de la collection

La collection est organisée en dossiers :

```
Parking API
├── 📊 Statut
│   ├── GET - Dernier statut
│   ├── GET - Statistiques (24h)
│   ├── GET - Historique (paginated)
│   ├── GET - Historique filtré par statut
│   ├── GET - Historique trié
│   └── GET - Détail d'un enregistrement
│
├── ✏️ Mise à jour
│   ├── POST - Mise à jour manuelle
│   ├── POST - Mise à jour (parking plein)
│   └── POST - Mise à jour (parking vide)
│
├── 📤 Upload Image
│   └── POST - Upload image ESP32-CAM
│
└── 🧪 Tests d'erreurs
    ├── POST - Erreur validation (occupied négatif)
    ├── POST - Erreur validation (données manquantes)
    ├── POST - Erreur upload (sans image)
    └── GET - Erreur 404 (ID inexistant)
```

## 🔍 Comment tester chaque endpoint

### 1. Tester le statut

**GET - Dernier statut**
- ✅ Le plus simple pour commencer
- Cliquez sur "Send"
- Vous devriez voir une réponse JSON ou un message si aucune donnée

**GET - Statistiques (24h)**
- Affiche les statistiques des dernières 24 heures
- Nécessite des données existantes

**GET - Historique**
- Affiche tous les enregistrements avec pagination
- Par défaut : page 1, 10 éléments par page
- Vous pouvez modifier les paramètres dans l'onglet "Params"

### 2. Créer des données

**POST - Mise à jour manuelle**
- Le body JSON est déjà configuré : `{"occupied": 8, "total_spaces": 15}`
- Cliquez sur "Send"
- Une nouvelle entrée est créée dans la base de données
- La réponse contient les détails de l'enregistrement créé

**Modifier les valeurs** :
- Cliquez sur l'onglet "Body"
- Modifiez les valeurs `occupied` et `total_spaces`
- Cliquez sur "Send"

### 3. Upload d'image

**POST - Upload image ESP32-CAM**
- Cliquez sur l'onglet "Body"
- Dans "form-data", cliquez sur "Select Files" à côté de `image`
- Sélectionnez une image JPEG
- Cliquez sur "Send"
- L'API détecte automatiquement les voitures avec YOLO

### 4. Tester les filtres et la pagination

**GET - Historique filtré**
- Modifiez le paramètre `status` dans l'onglet "Params"
- Valeurs possibles : `available` ou `full`

**GET - Historique trié**
- Modifiez le paramètre `ordering` dans l'onglet "Params"
- Valeurs possibles :
  - `-timestamp` (du plus récent au plus ancien)
  - `timestamp` (du plus ancien au plus récent)
  - `-occupancy_rate` (du plus occupé au moins occupé)
  - `occupancy_rate` (du moins occupé au plus occupé)

### 5. Tester la gestion d'erreurs

Les requêtes dans "Tests d'erreurs" permettent de vérifier que :
- Les validations fonctionnent correctement
- Les erreurs sont bien renvoyées
- Les codes HTTP sont corrects (400, 404, etc.)

## 💡 Astuces Postman

### Variables dans les URLs

Toutes les requêtes utilisent `{{base_url}}` qui peut être :
- Défini dans les variables de collection
- Défini dans un environnement
- Si vous créez de nouvelles requêtes, utilisez `{{base_url}}` au lieu de l'URL complète

### Exemples de réponses

Regardez l'onglet "Examples" dans Postman pour voir des exemples de réponses (après avoir envoyé quelques requêtes).

### Tests automatiques

Vous pouvez ajouter des scripts de test dans l'onglet "Tests" :

```javascript
// Vérifier le statut HTTP
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Vérifier la structure de la réponse
pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('occupied');
    pm.expect(jsonData).to.have.property('available');
    pm.expect(jsonData).to.have.property('status');
});

// Vérifier les valeurs
pm.test("Occupied is between 0 and total_spaces", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.occupied).to.be.at.least(0);
    pm.expect(jsonData.occupied).to.be.at.most(jsonData.total_spaces);
});
```

### Sauvegarder des réponses

- Après avoir envoyé une requête, vous pouvez cliquer sur "Save Response"
- Utile pour documenter ou partager des exemples

### Partager la collection

- Cliquez sur la collection → "..." → "Export"
- Partagez le fichier JSON avec votre équipe

## 🔧 Dépannage

### Erreur : "Could not get any response"

**Causes possibles** :
1. Le serveur Django n'est pas démarré
   - Solution : `python manage.py runserver`
2. Mauvaise URL
   - Vérifiez que `base_url` est correct dans les variables

### Erreur : 404 Not Found

**Causes possibles** :
1. Mauvaise route
   - Vérifiez que l'URL est : `{{base_url}}/status/latest/` (avec le `/` à la fin)
2. Le serveur n'a pas les migrations appliquées
   - Solution : `python manage.py migrate`

### Erreur : 500 Internal Server Error

**Causes possibles** :
1. Problème avec la base de données
   - Vérifiez les logs du serveur Django
2. Module manquant
   - Vérifiez que tous les packages sont installés : `pip install -r requirements.txt`

### Les variables ne fonctionnent pas

**Solution** :
- Assurez-vous que l'environnement est sélectionné (si vous utilisez les environnements)
- Ou vérifiez les variables de la collection

## 📚 Ressources

- [Documentation Postman](https://learning.postman.com/docs/)
- [Guide complet des API](./API_TESTING_GUIDE.md)
- [Démarrage rapide](./TEST_QUICKSTART.md)
