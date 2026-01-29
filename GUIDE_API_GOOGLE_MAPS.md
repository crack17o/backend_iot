# 🗺️ Guide d'Activation de l'API Google Maps

## 📋 Prérequis

- Un compte Google (Gmail)
- Une carte bancaire (pour la facturation, mais Google offre des crédits gratuits)

---

## 🚀 Étapes détaillées

### Étape 1 : Accéder à Google Cloud Console

1. Ouvrez votre navigateur et allez sur : **[https://console.cloud.google.com/](https://console.cloud.google.com/)**
2. Connectez-vous avec votre compte Google

---

### Étape 2 : Créer un nouveau projet (ou utiliser un existant)

1. En haut de la page, cliquez sur le **sélecteur de projet** (à côté de "Google Cloud")
2. Cliquez sur **"Nouveau projet"**
3. Remplissez les informations :
   - **Nom du projet** : `Parking Intelligence` (ou un nom de votre choix)
   - **Organisation** : Laissez par défaut (si applicable)
4. Cliquez sur **"Créer"**
5. Attendez quelques secondes que le projet soit créé
6. Sélectionnez le projet nouvellement créé dans le sélecteur de projet

---

### Étape 3 : Activer l'API Directions

1. Dans le menu de gauche, allez dans **"APIs & Services"** > **"Library"** (Bibliothèque)
2. Dans la barre de recherche, tapez : **"Directions API"**
3. Cliquez sur **"Directions API"** dans les résultats
4. Cliquez sur le bouton **"Enable"** (Activer)
5. Attendez quelques secondes que l'API soit activée

**Note :** Vous pouvez aussi activer **"Maps JavaScript API"** si vous prévoyez d'utiliser des cartes interactives dans le futur.

---

### Étape 4 : Créer une clé API

1. Dans le menu de gauche, allez dans **"APIs & Services"** > **"Credentials"** (Identifiants)
2. En haut de la page, cliquez sur **"+ CREATE CREDENTIALS"** (Créer des identifiants)
3. Sélectionnez **"API key"** (Clé API)
4. Une clé API sera générée automatiquement
5. **⚠️ IMPORTANT :** Cliquez sur **"Restrict key"** (Restreindre la clé) pour la sécurité

---

### Étape 5 : Restreindre la clé API (Recommandé pour la sécurité)

1. Dans la section **"API restrictions"** :
   - Sélectionnez **"Restrict key"**
   - Dans la liste déroulante, sélectionnez **"Directions API"**
   - Cliquez sur **"OK"**

2. Dans la section **"Application restrictions"** (optionnel mais recommandé) :
   - Pour un serveur backend, sélectionnez **"IP addresses"** (Adresses IP)
   - Ajoutez l'adresse IP de votre serveur (ou laissez vide pour le développement local)

3. Cliquez sur **"Save"** (Enregistrer)

---

### Étape 6 : Copier la clé API

1. Retournez à la page **"Credentials"**
2. Trouvez votre clé API dans la liste
3. Cliquez sur l'icône **copier** à côté de la clé
4. **⚠️ Gardez cette clé secrète !** Ne la partagez jamais publiquement

---

### Étape 7 : Configurer la clé dans votre projet

#### Option A : Via l'interface web (si disponible)

1. Connectez-vous au dashboard : `http://localhost:8000/`
2. Allez dans **"Paramètres"**
3. Collez la clé API dans le champ approprié (si cette fonctionnalité existe)

#### Option B : Via le fichier constants.py (Recommandé)

1. Ouvrez le fichier : `parking/parking_monitor/utils/constants.py`
2. Trouvez la ligne :
   ```python
   GOOGLE_MAPS_API_KEY = "VOTRE_CLE_API_GOOGLE_MAPS"
   ```
3. Remplacez `"VOTRE_CLE_API_GOOGLE_MAPS"` par votre clé API :
   ```python
   GOOGLE_MAPS_API_KEY = "AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```
4. Sauvegardez le fichier

---

### Étape 8 : Activer la facturation (Nécessaire pour utiliser l'API)

1. Dans Google Cloud Console, allez dans **"Billing"** (Facturation) dans le menu
2. Cliquez sur **"Link a billing account"** (Lier un compte de facturation)
3. Suivez les instructions pour ajouter une carte bancaire
4. **Note :** Google offre **$200 de crédits gratuits par mois** pour les nouvelles utilisations
   - Les premières 40 000 requêtes Directions API sont gratuites par mois
   - Au-delà, c'est environ $5 pour 1000 requêtes supplémentaires

---

## ✅ Vérification

### Tester que l'API fonctionne

1. Démarrez votre serveur Django :
   ```bash
   cd parking
   python manage.py runserver
   ```

2. Connectez-vous au dashboard : `http://localhost:8000/`

3. Allez dans **"Situation Live"** ou **"Historique Trafic"**

4. Cliquez sur **"Vérifier Trafic Aller"** ou **"Vérifier Trafic Retour"**

5. Si tout fonctionne, vous devriez voir les données de trafic s'afficher !

---

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne commitez jamais votre clé API dans Git**
   - Ajoutez `constants.py` au `.gitignore` si elle contient des secrets
   - Ou utilisez des variables d'environnement

2. **Restreignez votre clé API**
   - Limitez-la à l'API Directions uniquement
   - Ajoutez des restrictions par adresse IP si possible

3. **Surveillez votre utilisation**
   - Allez dans **"APIs & Services"** > **"Dashboard"** pour voir votre consommation
   - Configurez des alertes de quota dans Google Cloud Console

---

## 💰 Coûts et quotas

### Crédits gratuits Google Cloud

- **$200 de crédits gratuits** par mois pour les nouveaux comptes
- **40 000 requêtes Directions API gratuites** par mois
- Au-delà : environ **$5 pour 1000 requêtes supplémentaires**

### Estimation pour votre projet

Si vous vérifiez le trafic :
- **Toutes les 5 minutes** : ~288 requêtes/jour = ~8 640 requêtes/mois ✅ Gratuit
- **Toutes les 1 minute** : ~1 440 requêtes/jour = ~43 200 requêtes/mois ⚠️ Dépassement du quota gratuit

**Recommandation :** Vérifiez le trafic toutes les 5-10 minutes pour rester dans le quota gratuit.

---

## 🐛 Dépannage

### Erreur : "API key not valid"

- Vérifiez que la clé API est correctement copiée (sans espaces)
- Vérifiez que l'API Directions est bien activée
- Vérifiez que la clé n'est pas restreinte à une IP différente

### Erreur : "This API project is not authorized to use this API"

- Allez dans **"APIs & Services"** > **"Library"**
- Recherchez "Directions API"
- Vérifiez que l'API est bien activée (bouton "Manage" au lieu de "Enable")

### Erreur : "Billing account required"

- Activez la facturation dans Google Cloud Console
- Ajoutez une carte bancaire (les crédits gratuits seront utilisés en premier)

### Erreur : "Quota exceeded"

- Vous avez dépassé le quota gratuit
- Attendez le mois suivant ou augmentez votre quota dans Google Cloud Console

---

## 📚 Ressources supplémentaires

- [Documentation officielle Directions API](https://developers.google.com/maps/documentation/directions)
- [Pricing Google Maps Platform](https://developers.google.com/maps/billing-and-pricing/pricing)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## ✅ Checklist finale

- [ ] Compte Google créé
- [ ] Projet Google Cloud créé
- [ ] API Directions activée
- [ ] Clé API créée
- [ ] Clé API restreinte (recommandé)
- [ ] Facturation activée
- [ ] Clé API configurée dans `constants.py`
- [ ] Test de l'API réussi

---

**Une fois ces étapes terminées, votre API Google Maps sera prête à être utilisée ! 🎉**
