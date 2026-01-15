@echo off
REM Script pour appliquer les migrations
cd parking
..\venv\Scripts\python.exe manage.py migrate
pause
