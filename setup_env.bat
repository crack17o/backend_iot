@echo off
REM Script pour creer et configurer l'environnement virtuel
echo ========================================
echo Configuration de l'environnement virtuel
echo ========================================
echo.

REM Creer l'environnement virtuel s'il n'existe pas
if not exist "venv" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
    echo [OK] Environnement virtuel cree
) else (
    echo L'environnement virtuel existe deja
)

echo.
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo Mise a jour de pip...
python -m pip install --upgrade pip

echo.
echo Installation des dependances...
pip install -r ./requirements.txt

echo.
echo ========================================
echo Configuration terminee !
echo ========================================
echo.
echo Pour activer l'environnement virtuel plus tard :
echo   activate_env.bat
echo   ou
echo   venv\Scripts\activate.bat
echo.
pause
