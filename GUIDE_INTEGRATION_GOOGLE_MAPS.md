# 🗺️ Guide d'Intégration de Google Maps pour la Visualisation

## 📋 Prérequis

- Clé API Google Maps configurée (voir `GUIDE_API_GOOGLE_MAPS.md`)
- API "Maps JavaScript API" activée dans Google Cloud Console

---

## 🚀 Étapes pour Activer la Carte

### Étape 1 : Activer l'API Maps JavaScript

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Sélectionnez votre projet
3. Allez dans **"APIs & Services"** > **"Library"**
4. Recherchez **"Maps JavaScript API"**
5. Cliquez sur **"Enable"** (Activer)

### Étape 2 : Configurer la Clé API

1. Ouvrez `parking/parking_monitor/utils/constants.py`
2. Vérifiez que votre clé API est configurée :
   ```python
   GOOGLE_MAPS_API_KEY = "VOTRE_CLE_API_ICI"
   ```

### Étape 3 : Redémarrer le Serveur

```bash
cd parking
python manage.py runserver
```

### Étape 4 : Accéder à la Page Live

1. Connectez-vous au dashboard
2. Allez sur **"Situation Live"**
3. La carte devrait s'afficher automatiquement

---

## 🎯 Fonctionnalités Implémentées

### ✅ Vérification Automatique du Trafic

- **Fréquence** : Toutes les 10 secondes
- **Alternance** : Vérifie le trafic "Aller" puis "Retour" alternativement
- **Mise à jour** : La page se rafraîchit automatiquement avec les nouvelles données

### ✅ Carte Interactive

- **Affichage** : Carte Google Maps centrée sur le trajet
- **Trajet** : Ligne tracée entre le point de départ et d'arrivée
- **Zoom** : Automatiquement ajusté pour voir tout le trajet
- **Marqueurs** : Points de départ et d'arrivée visibles

---

## 🔧 Configuration Avancée

### Modifier la Fréquence de Vérification

Dans `parking/templates/live_situation.html`, modifiez la ligne :

```javascript
}, 10000); // 10 secondes (changez 10000 pour une autre valeur en millisecondes)
```

Exemples :
- 5 secondes : `5000`
- 30 secondes : `30000`
- 1 minute : `60000`

### Personnaliser la Carte

Dans la fonction `initMap()`, vous pouvez modifier :

```javascript
map = new google.maps.Map(document.getElementById('map'), {
    zoom: 15,  // Niveau de zoom (1-20)
    center: { lat: (startLat + endLat) / 2, lng: (startLng + endLng) / 2 },
    mapTypeId: 'roadmap'  // 'roadmap', 'satellite', 'hybrid', 'terrain'
});
```

---

## 🐛 Dépannage

### La carte ne s'affiche pas

1. **Vérifiez la clé API** :
   - Allez dans `constants.py`
   - Vérifiez que `GOOGLE_MAPS_API_KEY` est bien configurée
   - Redémarrez le serveur Django

2. **Vérifiez les APIs activées** :
   - Maps JavaScript API doit être activée
   - Directions API doit être activée (pour le trafic)

3. **Vérifiez la console du navigateur** :
   - Ouvrez les outils développeur (F12)
   - Regardez l'onglet "Console" pour les erreurs
   - Erreur commune : "This API project is not authorized to use this API"

### La vérification automatique ne fonctionne pas

1. **Vérifiez la console du navigateur** :
   - Ouvrez les outils développeur (F12)
   - Regardez l'onglet "Console" pour les erreurs

2. **Vérifiez que vous êtes connecté** :
   - La vérification nécessite une session active
   - Reconnectez-vous si nécessaire

3. **Vérifiez les permissions** :
   - Seuls les administrateurs peuvent vérifier le trafic
   - Vérifiez que votre compte est admin

---

## 💰 Coûts

### Maps JavaScript API

- **Gratuit** : 28 000 chargements de carte par mois
- **Au-delà** : $7 pour 1000 chargements supplémentaires

### Directions API

- **Gratuit** : 40 000 requêtes par mois
- **Au-delà** : $5 pour 1000 requêtes supplémentaires

**Note** : Avec une vérification toutes les 10 secondes :
- ~8 640 requêtes/jour = ~259 200 requêtes/mois
- Cela dépasse le quota gratuit, mais reste dans les crédits gratuits de $200/mois

---

## 📚 Ressources

- [Documentation Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [Documentation Directions API](https://developers.google.com/maps/documentation/directions)
- [Pricing Google Maps Platform](https://developers.google.com/maps/billing-and-pricing/pricing)

---

## ✅ Checklist

- [ ] Clé API Google Maps configurée
- [ ] Maps JavaScript API activée
- [ ] Directions API activée
- [ ] Serveur Django redémarré
- [ ] Carte visible sur la page "Situation Live"
- [ ] Vérification automatique fonctionnelle (toutes les 10 secondes)

---

**Une fois ces étapes terminées, la carte et la vérification automatique seront opérationnelles ! 🎉**
