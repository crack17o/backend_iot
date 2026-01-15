# Guide d'utilisation de l'environnement virtuel

## 🎯 Pourquoi utiliser un environnement virtuel ?

Un environnement virtuel isole les dépendances de votre projet pour éviter les conflits entre différents projets Python.

## 📦 Installation initiale

### Option 1 : Script automatique (recommandé)
```bash
setup_env.bat
```

Ce script va :
- Créer l'environnement virtuel `venv/`
- Activer l'environnement
- Mettre à jour pip
- Installer toutes les dépendances depuis `requirements.txt`

### Option 2 : Manuellement
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate.bat

# Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Utilisation quotidienne

### Activer l'environnement virtuel

**Windows (CMD) :**
```bash
venv\Scripts\activate.bat
```
ou double-cliquez sur `activate_env.bat`

**Windows (PowerShell) :**
```powershell
venv\Scripts\Activate.ps1
```

**Linux/Mac :**
```bash
source venv/bin/activate
```

### Vérifier que l'environnement est activé

Quand l'environnement est activé, vous verrez `(venv)` au début de votre ligne de commande :
```
(venv) PS D:\...\backend_iot>
```

### Désactiver l'environnement virtuel
```bash
deactivate
```

## 📝 Commandes utiles

### Installer une nouvelle dépendance
```bash
# Activer l'environnement d'abord
venv\Scripts\activate.bat

# Installer le package
pip install nom_du_package

# Mettre à jour requirements.txt
pip freeze > requirements.txt
```

### Réinstaller toutes les dépendances
```bash
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Voir les packages installés
```bash
venv\Scripts\activate.bat
pip list
```

## ⚠️ Important

- **Toujours activer l'environnement virtuel** avant de travailler sur le projet
- **Ne jamais commiter** le dossier `venv/` (déjà dans `.gitignore`)
- **Mettre à jour `requirements.txt`** quand vous installez de nouveaux packages

## 🔧 Résolution de problèmes

### L'environnement virtuel ne s'active pas
- Vérifiez que vous êtes dans le bon répertoire
- Sur PowerShell, vous devrez peut-être autoriser l'exécution de scripts :
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Les packages ne sont pas trouvés
- Vérifiez que l'environnement virtuel est bien activé (vous devriez voir `(venv)`)
- Réinstallez les dépendances : `pip install -r requirements.txt`
