@echo off
echo ============================================================
echo   PREMIUM INTELLIGENT ADAPTIVE TRADING AGENT
echo   Starting All Systems...
echo ============================================================
echo.

REM Verify VENV exists
if not exist ".venv" (
    echo Virtual Environment not found!
    echo Please run 'setup_env.bat' first to install dependencies.
    pause
    exit /b
)

echo [1/3] Starting Database (PostgreSQL)...
docker start forex_db >nul 2>&1
if %errorlevel% neq 0 (
    echo Database container not found. Creating new container...
    docker run --name forex_db -e POSTGRES_USER=forex_admin -e POSTGRES_PASSWORD=forex_secure_2024 -e POSTGRES_DB=forex_agent -p 5433:5432 -d postgres:15-alpine
    timeout /t 5 /nobreak >nul
    echo Database initialized successfully.
) else (
    echo Database already running.
)

echo [2/3] Initializing Database Schema...
REM Explicitly use the VENV python
.venv\Scripts\python src/database/models.py
if %errorlevel% neq 0 (
    echo Error initializing database schema!
    pause
    exit /b
)

echo [3/3] Starting Trading Agent and Dashboard...
echo.
echo ============================================================
echo   Dashboard will open in your browser automatically
echo   Trading Agent is running in the background window
echo ============================================================
echo.

REM Start Agent in separate window using VENV python
start "Trading Agent" cmd /k ".venv\Scripts\python -m src.main"

timeout /t 3 /nobreak >nul

REM Start Dashboard using VENV python module
.venv\Scripts\python -m streamlit run src/dashboard/app.py

pause
