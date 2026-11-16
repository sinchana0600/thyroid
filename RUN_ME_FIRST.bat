@echo off
color 0A
echo ========================================
echo   THYROID DETECTION SYSTEM SETUP
echo ========================================
echo.

echo [1/3] Setting up database...
python setup_database.py
if errorlevel 1 (
    echo.
    echo ERROR: Database setup failed!
    echo Please check MySQL is running and password is correct.
    pause
    exit /b 1
)

echo.
echo [2/3] Testing backend connection...
python test_backend.py
if errorlevel 1 (
    echo.
    echo ERROR: Backend test failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Starting application...
echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Backend is running on: http://localhost:5000
echo.
echo Opening frontend in your browser...
timeout /t 2 /nobreak > nul
start frontend\index.html

echo.
echo ========================================
echo   APPLICATION IS READY TO USE!
echo ========================================
echo.
echo Instructions:
echo 1. Click "Patient" button
echo 2. Register a new account
echo 3. Login and explore features
echo.
echo Keep this window open (backend is running here)
echo Press Ctrl+C to stop the server
echo.
pause
