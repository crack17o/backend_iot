#!/bin/bash

echo "==================================="
echo "   PARKING INTELLIGENCE - Setup"
echo "==================================="
echo ""

# Vérifier si venv existe
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    echo ""
fi

# Activer venv
echo "Activation de l'environnement virtuel..."
source venv/bin/activate
echo ""

# Installer les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt
echo ""

# Faire les migrations
echo "Préparation de la base de données..."
cd parking
python manage.py migrate
cd ..
echo ""

echo "==================================="
echo "   Setup terminé !"
echo "==================================="
echo ""
echo "Pour démarrer :"
echo "   1. Terminal 1 : cd parking && python manage.py runserver"
echo "   2. Terminal 2 : python counter.py videos/test.mp4"
echo ""
