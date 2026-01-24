@echo off
echo PREPARING PREMIUM ENVIRONMENT...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found.
    exit /b
)

if not exist ".venv" (
    echo Creating .venv...
    python -m venv .venv
)

echo Upgrading PIP...
.venv\Scripts\python -m pip install --upgrade pip

echo Installing dependencies...
.venv\Scripts\python -m pip install -r requirements.txt

echo.
echo SETUP COMPLETE.
pause
