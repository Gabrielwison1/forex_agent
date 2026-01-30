@echo off
echo ============================================================
echo   PREMIUM DASHBOARD
echo   Launching Streamlit Interface
echo ============================================================
echo.

REM Set Python path
set PYTHONPATH=.

REM Check if venv python exists
if exist ".venv\Scripts\python.exe" (
    set START_CMD=.venv\Scripts\streamlit.exe
    echo Using virutal environment Streamlit
) else (
    set START_CMD=streamlit
    echo WARNING: Virtual environment not found, using system Streamlit
)

REM Run the dashboard
echo Starting Dashboard...
%START_CMD% run src/dashboard/app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Dashboard crashed.
    pause
)
