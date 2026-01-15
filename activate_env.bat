@echo off
REM Script pour activer l'environnement virtuel sur Windows
call venv\Scripts\activate.bat
echo Environnement virtuel active !
echo.
echo Pour installer les dependances :
echo   pip install -r requirements.txt
echo.
echo Pour desactiver l'environnement virtuel :
echo   deactivate
cmd /k
