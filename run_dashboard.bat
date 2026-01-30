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
    set PYTHON_CMD=.venv\Scripts\python.exe
    echo Using virtual environment Python
) else (
    set PYTHON_CMD=python
    echo WARNING: Virtual environment not found, using system Python
)

REM Run the dashboard using python -m streamlit
echo Starting Dashboard...
%PYTHON_CMD% -m streamlit run src/dashboard/app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Dashboard crashed.
    pause
)
