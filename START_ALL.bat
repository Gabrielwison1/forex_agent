@echo off
echo ============================================================
echo   PREMIUM FX AGENT - MASTER STARTUP
echo   Complete System Launch
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_env.bat first to create the virtual environment.
    pause
    exit /b 1
)

echo [1/5] Activating virtual environment...
REM Note: activate.bat doesn't work in batch files, but dependencies are installed in .venv
REM We'll use python from .venv directly in commands below
set PYTHON=.venv\Scripts\python.exe

if not exist "%PYTHON%" (
    echo ERROR: Python not found in virtual environment!
    echo Please run setup_env.bat to reinstall dependencies.
    pause
    exit /b 1
)

echo Virtual environment detected. Using: %PYTHON%

echo.
echo [2/5] Starting PostgreSQL database...

REM Check if container already exists and is running
docker ps -a --filter "name=forex_db" --format "{{.Names}}" | findstr "forex_db" >nul
if %errorlevel% equ 0 (
    echo Container 'forex_db' already exists. Checking status...
    
    REM Check if it's running
    docker ps --filter "name=forex_db" --format "{{.Names}}" | findstr "forex_db" >nul
    if %errorlevel% equ 0 (
        echo Database is already running.
    ) else (
        echo Starting existing container...
        docker start forex_db
    )
) else (
    echo Creating new database container...
    start /min cmd /c run_db.bat
    echo Waiting for database to initialize...
    timeout /t 5 /nobreak >nul
)

echo.
echo [3/5] Initializing database tables...
set PYTHONPATH=.
%PYTHON% -c "from src.database.models import init_db; init_db(); print('Database initialized successfully')"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to initialize database!
    echo This usually means dependencies are not installed.
    echo.
    echo To fix this, run: .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [4/5] Enabling trading (kill switch)...
%PYTHON% -c "from src.safety.kill_switch import enable_trading; enable_trading()"

echo.
echo [5/5] Starting components...
echo.
echo ============================================================
echo   SYSTEM READY
echo ============================================================
echo.
echo The following services will start:
echo   - Trading Agent (main window)
echo   - Exit Monitor (background - monitors closed positions)
echo   - Dashboard (opens in browser at http://localhost:8501)
echo.
echo Press any key to launch all components...
pause >nul

echo.
echo [STARTING] Trading Agent...
start "Trading Agent" cmd /c START_AGENT.bat

echo [STARTING] Exit Monitor...
start "Exit Monitor" cmd /c run_exit_monitor.bat

echo [STARTING] Dashboard...
start "Dashboard" cmd /c run_dashboard.bat

echo.
echo ============================================================
echo   ALL SYSTEMS OPERATIONAL
echo ============================================================
echo.
echo Windows opened:
echo   1. Trading Agent - Main execution loop
echo   2. Exit Monitor - Position tracking
echo   3. Dashboard - Web interface at http://localhost:8501
echo.
echo To stop all services:
echo   1. Close all command windows OR
echo   2. Press Ctrl+C in each window
echo.
echo PostgreSQL is running in Docker container 'forex_db'
echo To stop it: docker stop forex_db
echo.
pause
