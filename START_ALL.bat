@echo off
echo ============================================================
echo   PREMIUM FX AGENT - MASTER STARTUP
echo   Complete System Launch
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_env.bat first.
    pause
    exit /b 1
)

echo [1/5] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [2/5] Starting PostgreSQL database...
start /min cmd /c run_db.bat

echo Waiting for database to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [3/5] Initializing database tables...
set PYTHONPATH=.
python -c "from src.database.models import init_db; init_db(); print('Database initialized successfully')"

echo.
echo [4/5] Enabling trading (kill switch)...
python -c "from src.safety.kill_switch import enable_trading; enable_trading()"

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
echo PostgreSQL is running in the background.
echo To stop it: docker stop postgres_trading
echo.
pause
