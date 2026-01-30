@echo off
echo ============================================================
echo   TRADE EXIT MONITOR
echo   Autonomous Position Tracking
echo ============================================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Set Python path
set PYTHONPATH=.

REM Run the exit monitor
echo Starting exit monitor (checks every 2 minutes)...
python src/monitoring/exit_monitor.py

pause
