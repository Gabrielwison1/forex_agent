@echo off
echo ============================================================
echo   PREMIUM INTELLIGENT ADAPTIVE TRADING AGENT
echo   Starting All Systems...
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

REM Run the agent
echo Starting Trading Agent...
%START_CMD% src/main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Agent crashed.
    pause
)
