@echo off
echo ============================================================
echo   TRADE EXIT MONITOR
echo   Autonomous Position Tracking
echo ============================================================
echo.

REM Set Python path
set PYTHONPATH=.

REM Check if venv python exists
if exist ".venv\Scripts\python.exe" (
    set START_CMD=.venv\Scripts\python.exe
    echo Using virtual environment Python
) else (
    set START_CMD=python
    echo WARNING: Virtual environment not found, using system Python
)

REM Run the exit monitor
echo Starting exit monitor (checks every 2 minutes)...
%START_CMD% src/monitoring/exit_monitor.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Exit monitor crashed.
    pause
)
