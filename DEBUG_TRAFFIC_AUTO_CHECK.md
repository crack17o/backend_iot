# 🔍 Guide de Débogage - Vérification Automatique du Trafic

## 🐛 Problème : La vérification automatique ne fonctionne pas

### ✅ Vérifications à faire

#### 1. Ouvrir la Console du Navigateur

1. Ouvrez la page "Situation Live" : `http://127.0.0.1:8000/live/`
2. Appuyez sur **F12** pour ouvrir les outils développeur
3. Allez dans l'onglet **"Console"**
4. Vous devriez voir des messages comme :
   - `=== Initialisation de la page Situation Live ===`
   - `✅ Token CSRF trouvé`
   - `Démarrage de la vérification automatique du trafic...`

#### 2. Vérifier les Erreurs dans la Console

**Si vous voyez :**
- `❌ Token CSRF non trouvé` → Reconnectez-vous
- `❌ Erreur lors de la vérification du trafic` → Voir section "Erreurs API"
- `Clé API Google Maps non configurée` → Configurez la clé API

#### 3. Vérifier la Clé API Google Maps

1. Ouvrez `parking/parking_monitor/utils/constants.py`
2. Vérifiez que `GOOGLE_MAPS_API_KEY` contient votre clé valide
3. Redémarrez le serveur Django

#### 4. Vérifier que l'API Directions est Activée

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services > Library
3. Recherchez "Directions API"
4. Vérifiez qu'elle est **activée** (bouton "Manage" visible)

#### 5. Tester Manuellement

Dans la console du navigateur, tapez :
```javascript
checkTraffic('aller');
```

Vous devriez voir :
- `Vérification du trafic aller...`
- `Réponse reçue: 200 OK` ou une erreur

---

## 🔧 Solutions aux Problèmes Courants

### Problème : "Token CSRF non trouvé"

**Solution :**
1. Reconnectez-vous au dashboard
2. Vérifiez que vous êtes bien authentifié
3. Rechargez la page

### Problème : "Clé API Google Maps non configurée"

**Solution :**
1. Configurez `GOOGLE_MAPS_API_KEY` dans `constants.py`
2. Redémarrez le serveur Django

### Problème : "Erreur API Google Maps: REQUEST_DENIED"

**Causes possibles :**
- La clé API n'est pas valide
- L'API Directions n'est pas activée
- La clé API est restreinte à certaines IPs

**Solution :**
1. Vérifiez la clé API dans Google Cloud Console
2. Activez l'API Directions
3. Vérifiez les restrictions de la clé API

### Problème : "Erreur HTTP 401" ou "Erreur HTTP 403"

**Causes possibles :**
- Vous n'êtes pas connecté
- Votre session a expiré
- Vous n'avez pas les permissions admin

**Solution :**
1. Reconnectez-vous
2. Vérifiez que votre compte est admin (`is_staff=True`)

### Problème : La vérification démarre mais échoue

**Vérifiez dans la console :**
1. Le message d'erreur exact
2. Le code de statut HTTP
3. La réponse JSON (si disponible)

---

## 📊 Vérifier que ça Fonctionne

### Indicateurs Visuels

1. **Point vert clignotant** : Devrait clignoter toutes les 10 secondes
2. **Badge "LIVE"** : Devrait apparaître sur les cartes de trafic après vérification
3. **Heure de dernière vérification** : Devrait se mettre à jour

### Dans la Console

Vous devriez voir toutes les 10 secondes :
```
Vérification automatique du trafic (aller)...
Vérification du trafic aller...
Réponse reçue: 200 OK
✅ Trafic vérifié avec succès: Trafic vérifié avec succès pour la direction aller!
```

### Dans la Base de Données

1. Allez dans l'admin Django : `http://127.0.0.1:8000/admin/`
2. Traffic Status > Vous devriez voir de nouveaux enregistrements toutes les 10 secondes

---

## 🧪 Test Manuel

Pour tester manuellement, ouvrez la console du navigateur et exécutez :

```javascript
// Tester la vérification
checkTraffic('aller');

// Vérifier l'intervalle
console.log('Intervalle actif:', trafficCheckInterval !== null);

// Vérifier le token CSRF
console.log('Token CSRF:', getCookie('csrftoken'));
```

---

## 📝 Logs à Surveiller

Dans la console, vous devriez voir :
- ✅ Messages de succès (vert)
- ❌ Messages d'erreur (rouge)
- ⚠️ Messages d'avertissement (jaune)

Si vous ne voyez aucun message, le JavaScript ne s'exécute peut-être pas.

---

## 🔄 Redémarrer la Vérification

Si la vérification s'arrête, rechargez la page ou exécutez dans la console :

```javascript
if (trafficCheckInterval) {
    clearInterval(trafficCheckInterval);
}
startAutoCheck();
```

---

**Si le problème persiste, vérifiez les logs du serveur Django pour voir les erreurs côté backend.**
