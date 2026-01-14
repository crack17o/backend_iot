@echo off
REM Script de démarrage complet du projet

echo ===================================
echo   PARKING INTELLIGENCE - Setup
echo ===================================
echo.

REM Vérifier si venv existe
if not exist "venv" (
    echo Création de l'environnement virtuel...
    python -m venv venv
    echo.
)

REM Activer venv
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo.

REM Installer les dépendances
echo Installation des dépendances...
pip install -r requirements.txt
echo.

REM Faire les migrations
echo Préparation de la base de données...
cd parking
python manage.py migrate
cd ..
echo.

echo ===================================
echo   Setup terminé !
echo ===================================
echo.
echo Pour démarrer :
echo   1. Terminal 1 : cd parking && python manage.py runserver
echo   2. Terminal 2 : python counter.py videos/test.mp4
echo.
pause
