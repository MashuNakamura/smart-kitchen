@echo off
REM Check if .env file exists and loop through it to set variables
if exist .env (
    echo Loading .env variables...
    for /f "usebackq tokens=1* delims== eol=#" %%A in (".env") do (
        set %%A=%%B
    )
)

REM Start the main application with waitress
echo Starting Waitress server...
waitress-serve --host 0.0.0.0 --port 5002 app:app &
python3 model_server.py