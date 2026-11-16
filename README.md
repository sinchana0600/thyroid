# Thyroid Cancer Detection System

A comprehensive web application for thyroid health management with patient portal, health checkups, and automated thyroid test analysis.

## 🚀 Quick Start (3 Steps)

1. **Make sure MySQL is running** with password: `Panda@2003`
2. **Double-click** `RUN_ME_FIRST.bat`
3. **Open** `frontend/index.html` in your browser

That's it! The application is ready to use.

## Features

### Patient Module
- **User Authentication**: Login and registration system
- **Dashboard**: Clean, professional health overview
- **About Us**: Information about the application
- **Health Checkup**: Personalized health tips based on:
  - Sleep hours and stress levels
  - Height and weight (BMI calculation)
  - Water intake and age
- **Thyroid Check**: Upload test report images for automatic TSH, T3, T4 detection
- **Appointments**: Book and manage appointments with doctors
- **Reports**: View and download thyroid test reports
- **Logout**: Secure session management

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: MySQL
- **OCR**: Tesseract for image text extraction

## Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- Tesseract OCR

### Database Setup

1. Install MySQL and create the database:
```sql
mysql -u root -p
```

2. Run the schema file:
```sql
source database/schema.sql
```

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Install Tesseract OCR:
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **Mac**: `brew install tesseract`

3. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Open `frontend/index.html` in a web browser, or use a local server:
```bash
cd frontend
python -m http.server 8000
```

2. Access the application at `http://localhost:8000`

## Usage

1. **Home Page**: Choose between Doctor or Patient portal
2. **Patient Registration**: Create a new account
3. **Patient Login**: Access your dashboard
4. **Dashboard Navigation**: Use the sidebar to access different features
5. **Health Checkup**: Enter your health metrics for personalized tips
6. **Thyroid Check**: Upload test report images for analysis
7. **Book Appointment**: Select a doctor and schedule an appointment
8. **View Appointments**: Manage your appointments
9. **Reports**: Access your thyroid test history

## Database Configuration

The database password is set to `Panda@2003` in `backend/app.py`. Update this if needed:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'thyroid_detection'
}
```

## Project Structure

```
├── frontend/
│   ├── index.html
│   ├── patient/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── dashboard.html
│   ├── css/
│   │   ├── home.css
│   │   ├── auth.css
│   │   └── dashboard.css
│   └── js/
│       ├── patient-login.js
│       ├── patient-register.js
│       └── patient-dashboard.js
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── uploads/
└── database/
    └── schema.sql
```

## API Endpoints

- `POST /api/patient/register` - Register new patient
- `POST /api/patient/login` - Patient login
- `GET /api/doctors` - Get all doctors
- `POST /api/appointments` - Book appointment
- `GET /api/appointments/<patient_id>` - Get patient appointments
- `DELETE /api/appointments/<appointment_id>` - Cancel appointment
- `POST /api/health-checkup` - Save health checkup
- `POST /api/thyroid-check` - Analyze thyroid report
- `GET /api/reports/<patient_id>` - Get patient reports
- `GET /api/reports/download/<report_id>` - Download report

## Notes

- Ensure MySQL service is running before starting the backend
- The thyroid analysis uses OCR which requires clear, readable test report images
- Sample doctors are pre-populated in the database
- All passwords are hashed for security

## License

This project is for educational purposes.
