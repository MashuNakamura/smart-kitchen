@echo off
REM Force the script to run from the current folder
cd /d "%~dp0"

REM Check if .env file exists and set variables
if exist .env (
    echo Loading .env variables...
    for /f "usebackq tokens=1* delims== eol=#" %%A in (".env") do (
        set %%A=%%B
    )
)

REM --- THE FIX: Use the specific venv python, not "python3" ---
echo Starting Model Server using VENV...
".\venv\Scripts\python.exe" model_server.py

pause