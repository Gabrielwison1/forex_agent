# Quick Fix Guide - Startup Issues

## Issue 1: Virtual Environment Not Activating

**Error**: `.venv\Scripts\activate.bat` is not recognized

**Root Cause**: The batch file can't use `activate.bat` - it's a known Windows batch limitation

**Fix Applied**: START_ALL.bat now uses `.venv\Scripts\python.exe` directly instead of trying to activate

---

## Issue 2: Docker Container Name Conflict

**Error**: Container name "/forex_db" is already in use

**Root Cause**: PostgreSQL container from previous run is still there

**Fix Applied**: START_ALL.bat now:

1. Checks if container exists
2. If running, uses it
3. If stopped, starts it
4. If missing, creates new one

---

## How to Start Fresh Right Now

### Step 1: Clean Up Existing Container

```cmd
docker stop forex_db
docker rm forex_db
```

### Step 2: Ensure Dependencies Installed

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 3: Run Fixed Startup Script

```cmd
START_ALL.bat
```

---

## Dashboard Settings Now Functional! ✅

The Settings Manager can now edit `.env` file directly:

1. **Open Dashboard**: http://localhost:8501
2. **Go to**: Settings Manager
3. **Expand**: Update OANDA Credentials or Update Google AI Key
4. **Enter**: New credentials
5. **Click**: Save button
6. **Restart**: Close all windows and run START_ALL.bat again

Changes are saved to `.env` file immediately!

---

## What Was Fixed

### START_ALL.bat

- ✅ Uses `.venv\Scripts\python.exe` directly (no activate needed)
- ✅ Detects and reuses existing Docker containers
- ✅ Better error messages
- ✅ Helpfulcommand to fix missing dependencies

### Settings Manager

- ✅ OANDA credentials actually save to .env
- ✅ Google API key actually saves to .env
- ✅ Shows helpful restart instructions
- ✅ Full path handling for .env file
