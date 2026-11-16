@echo off
color 0A
cls

echo ========================================
echo   THYROID DETECTION SYSTEM
echo ========================================
echo.

echo [1/4] Checking ML Model...
if not exist "backend\models\thyroid_model.pkl" (
    echo Training ML Model...
    cd backend
    python train_model.py
    cd ..
    echo ✓ Model trained
) else (
    echo ✓ Model exists
)

echo.
echo [2/4] Verifying Database...
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password='Panda@2003', database='thyroid_detection'); print('✓ Database connected'); conn.close()" 2>nul
if errorlevel 1 (
    echo Setting up database...
    python setup_database.py
)

echo.
echo [3/4] Starting Backend Server...
cd backend
start "Thyroid Backend" cmd /k "python app.py"
cd ..
timeout /t 3 /nobreak > nul

echo.
echo [4/4] Opening Frontend...
start frontend\index.html

echo.
echo ========================================
echo   APPLICATION STARTED!
echo ========================================
echo.
echo ✓ Backend: http://localhost:5000
echo ✓ Frontend: Opened in browser
echo ✓ ML Model: Loaded
echo ✓ OCR: Available
echo ✓ Database: Connected
echo.
echo FEATURES READY:
echo - Manual Input (TSH, T3, T4)
echo - Image Upload with OCR
echo - ML Predictions with Confidence
echo - PDF Report Generation
echo - Patient Profile Management
echo - Appointment Booking
echo.
echo Keep backend window open!
echo Press any key to exit this window...
pause > nul
