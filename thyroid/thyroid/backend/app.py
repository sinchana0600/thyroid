from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import re
import pickle
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Import email service
try:
    from email_service import (send_email, send_registration_email, send_login_notification,
                               send_health_checkup_email, send_thyroid_report_email,
                               send_appointment_booking_email, send_appointment_status_email)
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    print("Warning: Email service not available")

# Optional OCR imports
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import cv2
    import numpy as np
    
    # Set Tesseract path explicitly for Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    OCR_AVAILABLE = True
    print("✓ OCR libraries available")
except ImportError as e:
    OCR_AVAILABLE = False
    print(f"Warning: OCR libraries not available ({e}). Manual input will be used.")
except Exception as e:
    OCR_AVAILABLE = False
    print(f"Warning: OCR setup error: {e}")

# Load ML model
try:
    with open('models/thyroid_model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('models/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    ML_AVAILABLE = True
    print("✓ ML model loaded successfully")
except:
    ML_AVAILABLE = False
    print("Warning: ML model not available. Using rule-based analysis.")

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Panda@2003',
    'database': 'thyroid_detection'
}

UPLOAD_FOLDER = '../uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Serve Frontend Files
@app.route('/')
def index():
    return send_file('../frontend/index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    try:
        return send_file(f'../frontend/{path}')
    except:
        return send_file('../frontend/index.html')

# Patient Registration
@app.route('/api/patient/register', methods=['POST'])
def register_patient():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = generate_password_hash(data['password'])
        
        # Check if email exists in doctors table
        cursor.execute("SELECT email FROM doctors WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            return jsonify({'message': 'Email already exists as doctor account'}), 400
        
        query = """INSERT INTO patients (full_name, email, password, phone, age, gender, address, 
                   security_question_1, security_answer_1, security_question_2, security_answer_2)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (data['full_name'], data['email'], hashed_password, 
                  data['phone'], data['age'], data['gender'], data.get('address', ''),
                  data.get('security_question_1', ''), data.get('security_answer_1', ''),
                  data.get('security_question_2', ''), data.get('security_answer_2', ''))
        
        cursor.execute(query, values)
        conn.commit()
        
        # Send welcome email
        if EMAIL_ENABLED:
            try:
                send_registration_email(data['full_name'], data['email'])
            except Exception as e:
                print(f"Email sending failed: {e}")
        
        return jsonify({'message': 'Registration successful'}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'message': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Patient Login
@app.route('/api/patient/login', methods=['POST'])
def login_patient():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM patients WHERE email = %s", (data['email'],))
        patient = cursor.fetchone()
        
        if patient and check_password_hash(patient['password'], data['password']):
            # Update last login timestamp
            cursor.execute("UPDATE patients SET last_login = NOW() WHERE patient_id = %s", 
                          (patient['patient_id'],))
            conn.commit()
            
            # Send login notification email
            if EMAIL_ENABLED:
                try:
                    send_login_notification(patient['full_name'], patient['email'])
                except Exception as e:
                    print(f"Email sending failed: {e}")
            
            return jsonify({
                'patient_id': patient['patient_id'],
                'full_name': patient['full_name'],
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    finally:
        cursor.close()
        conn.close()

# Password Reset - Step 1: Verify Email and Get Security Questions
@app.route('/api/patient/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT patient_id, full_name, security_question_1, security_question_2 FROM patients WHERE email = %s", (email,))
        patient = cursor.fetchone()
        
        if patient:
            if patient['security_question_1'] and patient['security_question_2']:
                return jsonify({
                    'success': True,
                    'patient_id': patient['patient_id'],
                    'security_question_1': patient['security_question_1'],
                    'security_question_2': patient['security_question_2'],
                    'message': 'Please answer both security questions'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Security questions not set. Please contact support.'
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': 'Email not found'
            }), 404
    finally:
        cursor.close()
        conn.close()

# Password Reset - Step 2: Verify Security Answers and Reset Password
@app.route('/api/patient/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    patient_id = data.get('patient_id')
    security_answer_1 = data.get('security_answer_1')
    security_answer_2 = data.get('security_answer_2')
    new_password = data.get('new_password')
    
    print(f"DEBUG: Reset request - patient_id: {patient_id}")
    print(f"DEBUG: Provided answers: '{security_answer_1}' | '{security_answer_2}'")
    print(f"DEBUG: New password length: {len(new_password) if new_password else 'None'}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT security_answer_1, security_answer_2 FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            print(f"DEBUG: Stored answers: '{patient['security_answer_1']}' | '{patient['security_answer_2']}'")
            answer1_match = patient['security_answer_1'].strip().lower() == security_answer_1.strip().lower()
            answer2_match = patient['security_answer_2'].strip().lower() == security_answer_2.strip().lower()
            print(f"DEBUG: Answer 1 match: {answer1_match}")
            print(f"DEBUG: Answer 2 match: {answer2_match}")
            
            if answer1_match and answer2_match:
                # Both security answers are correct, update password
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE patients SET password = %s WHERE patient_id = %s", 
                              (hashed_password, patient_id))
                conn.commit()
                print("DEBUG: Password updated successfully")
                
                return jsonify({
                    'success': True,
                    'message': 'Password reset successful! You can now login with your new password.'
                }), 200
            else:
                print("DEBUG: Security answers don't match")
                return jsonify({
                    'success': False,
                    'message': 'Incorrect security answers. Both answers must be correct.'
                }), 400
        else:
            print("DEBUG: Patient not found")
            return jsonify({
                'success': False,
                'message': 'Patient not found.'
            }), 400
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500
    finally:
        cursor.close()
        conn.close()

# Doctor Password Reset - Step 1: Verify Email and Get Security Questions
@app.route('/api/doctor/forgot-password', methods=['POST'])
def doctor_forgot_password():
    data = request.json
    email = data.get('email')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT doctor_id, full_name, security_question_1, security_question_2 FROM doctors WHERE email = %s", (email,))
        doctor = cursor.fetchone()
        
        if doctor:
            if doctor['security_question_1'] and doctor['security_question_2']:
                return jsonify({
                    'success': True,
                    'doctor_id': doctor['doctor_id'],
                    'security_question_1': doctor['security_question_1'],
                    'security_question_2': doctor['security_question_2'],
                    'message': 'Please answer both security questions'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Security questions not set. Please contact support.'
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': 'Email not found'
            }), 404
    finally:
        cursor.close()
        conn.close()

# Doctor Password Reset - Step 2: Verify Security Answers and Reset Password
@app.route('/api/doctor/reset-password', methods=['POST'])
def doctor_reset_password():
    data = request.json
    doctor_id = data.get('doctor_id')
    security_answer_1 = data.get('security_answer_1')
    security_answer_2 = data.get('security_answer_2')
    new_password = data.get('new_password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT security_answer_1, security_answer_2 FROM doctors WHERE doctor_id = %s", (doctor_id,))
        doctor = cursor.fetchone()
        
        if doctor and doctor['security_answer_1'].lower() == security_answer_1.lower() and doctor['security_answer_2'].lower() == security_answer_2.lower():
            # Both security answers are correct, update password
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE doctors SET password = %s WHERE doctor_id = %s", 
                          (hashed_password, doctor_id))
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Password reset successful! You can now login with your new password.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Incorrect security answers. Both answers must be correct.'
            }), 400
    finally:
        cursor.close()
        conn.close()

# Get Doctors
@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()
        return jsonify(doctors), 200
    finally:
        cursor.close()
        conn.close()

# Book Appointment
@app.route('/api/appointments', methods=['POST'])
def book_appointment():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the slot is already booked for the same doctor, date, and time
        doctor_conflict_query = """
            SELECT COUNT(*) FROM appointments 
            WHERE doctor_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s 
            AND status != 'Cancelled'
        """
        cursor.execute(doctor_conflict_query, (
            data['doctor_id'], 
            data['appointment_date'], 
            data['appointment_time']
        ))
        
        doctor_appointments = cursor.fetchone()[0]
        
        if doctor_appointments > 0:
            return jsonify({
                'message': 'This slot is already booked with this doctor. Please choose another slot. Thank you!'
            }), 409  # Conflict status code
        
        # Check if the same patient already has an appointment at the same date and time (with any doctor)
        patient_conflict_query = """
            SELECT COUNT(*) FROM appointments 
            WHERE patient_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s 
            AND status != 'Cancelled'
        """
        cursor.execute(patient_conflict_query, (
            data['patient_id'], 
            data['appointment_date'], 
            data['appointment_time']
        ))
        
        patient_appointments = cursor.fetchone()[0]
        
        if patient_appointments > 0:
            return jsonify({
                'message': 'You already have an appointment at this time. Please choose a different time slot. Thank you!'
            }), 409  # Conflict status code
        
        # If no conflict, proceed with booking
        query = """INSERT INTO appointments (patient_id, doctor_id, appointment_date, 
                   appointment_time, notes) VALUES (%s, %s, %s, %s, %s)"""
        values = (data['patient_id'], data['doctor_id'], data['appointment_date'],
                  data['appointment_time'], data.get('notes', ''))
        
        cursor.execute(query, values)
        conn.commit()
        
        # Send appointment booking email
        if EMAIL_ENABLED:
            try:
                # Get patient and doctor details
                cursor.execute("SELECT full_name, email FROM patients WHERE patient_id = %s", (data['patient_id'],))
                patient = cursor.fetchone()
                cursor.execute("SELECT full_name FROM doctors WHERE doctor_id = %s", (data['doctor_id'],))
                doctor = cursor.fetchone()
                
                if patient and doctor:
                    send_appointment_booking_email(
                        patient[0],  # patient_name
                        patient[1],  # patient_email
                        doctor[0],   # doctor_name
                        data['appointment_date'],
                        'Pending'
                    )
            except Exception as e:
                print(f"Email sending failed: {e}")
        
        return jsonify({'message': 'Appointment booked successfully'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Get Patient Appointments
@app.route('/api/appointments/<int:patient_id>', methods=['GET'])
def get_appointments(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """SELECT a.*, d.full_name as doctor_name, d.specialization 
                   FROM appointments a 
                   JOIN doctors d ON a.doctor_id = d.doctor_id 
                   WHERE a.patient_id = %s 
                   ORDER BY a.appointment_date DESC, a.appointment_time DESC"""
        cursor.execute(query, (patient_id,))
        appointments = cursor.fetchall()
        
        # Convert date and time to string
        for apt in appointments:
            apt['appointment_date'] = str(apt['appointment_date'])
            apt['appointment_time'] = str(apt['appointment_time'])
        
        return jsonify(appointments), 200
    finally:
        cursor.close()
        conn.close()

# Delete Appointment
@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE appointments SET status = 'Cancelled' WHERE appointment_id = %s", 
                      (appointment_id,))
        conn.commit()
        return jsonify({'message': 'Appointment cancelled'}), 200
    finally:
        cursor.close()
        conn.close()

# Health Checkup
@app.route('/api/health-checkup', methods=['POST'])
def health_checkup():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """INSERT INTO health_checkups (patient_id, sleep_hours, working_hours, 
                   height, weight, water_intake, health_tip) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (data['patient_id'], data['sleep_hours'], data['working_hours'],
                  data['height'], data['weight'], data['water_intake'], data['health_tip'])
        
        cursor.execute(query, values)
        conn.commit()
        
        # Send health checkup email
        if EMAIL_ENABLED:
            try:
                # Get patient email
                cursor.execute("SELECT full_name, email FROM patients WHERE patient_id = %s", (data['patient_id'],))
                patient = cursor.fetchone()
                if patient:
                    send_health_checkup_email(patient[0], patient[1], data)
            except Exception as e:
                print(f"Email sending failed: {e}")
        
        return jsonify({'message': 'Checkup saved'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Enhanced TSH extraction with better decimal handling
def extract_value(text, hormone):
    # Enhanced patterns to handle various report formats with better decimal precision
    # Patterns are ordered by specificity to avoid matching reference ranges
    patterns = [
        # Pattern 1: Value with unit immediately after (most specific)
        rf'{hormone}\s*\([^)]+\)\s+(\d+\.?\d*)\s+(?:µIU|mIU|uIU|plU|pIU|ng|µg|ug|mlU|mU)',
        # Pattern 2: "Observed Value" column format
        rf'{hormone}.*?(?:Observed|observed)\s+(?:Value|value)\s+(\d+\.?\d*)',
        # Pattern 3: Table format with value before unit
        rf'{hormone}[^0-9\n]*?(\d+\.?\d*)\s+(?:µIU|mIU|uIU|plU|pIU|ng|µg|ug|mlU|mU)(?:\s|/)',
        # Pattern 4: Simple format with colon
        rf'{hormone}\s*:\s*(\d+\.?\d*)\s+(?:µIU|mIU|uIU|plU|pIU|ng|µg|ug|mlU|mU)',
        # Pattern 5: Value on same line, not in range format
        rf'{hormone}\s*\([^)]+\)\s+(\d+\.?\d*)(?!\s*-\s*\d)',
        # Pattern 6: With equals or dash
        rf'{hormone}\s*[-=]\s*(\d+\.?\d*)\s+(?:µIU|mIU|uIU|plU|pIU|ng|µg|ug|mlU|mU)',
        # Pattern 7: Serum format
        rf'(?:Serum\s+)?{hormone}\s*:\s*(\d+\.?\d*)',
        # Pattern 8: Integer values with units
        rf'{hormone}\s+(\d+)\s+(?:µIU|mIU|uIU|plU|pIU|ng|µg|ug|mlU|mU)',
        # Pattern 9: Lowercase with units
        rf'{hormone.lower()}\s*:\s*(\d+\.?\d*)\s+(?:µIU|mIU|uIU|plU|pIU|ng|µg|ug|mlU|mU)',
        # Pattern 10: With comma as decimal (European)
        rf'{hormone}\s*\([^)]+\)\s+(\d+,\d+)\s+(?:µIU|mIU|uIU|plU|pIU)',
    ]
    
    # First, try to find the value in the "Observed Value" section
    # This is more reliable than general patterns
    observed_section = re.search(
        rf'{hormone}\s*\([^)]+\).*?(\d+\.?\d*)\s+(?:µIU|mIU|uIU|plU|pIU|ng|µg|ug|mlU|mU|we).*?(?:Biological|Reference)',
        text, re.IGNORECASE | re.DOTALL
    )
    if observed_section:
        try:
            value = float(observed_section.group(1))
            if 0.001 <= value <= 50:
                return value
        except (ValueError, IndexError):
            pass
    
    # Special handling for T3 and T4 which might have different formats
    if hormone in ['T3', 'T4']:
        print(f"  Searching for {hormone} with specialized patterns...")
        
        # COMPREHENSIVE T3/T4 specific patterns
        t3_t4_patterns = [
            # Specific patterns for table format with multiple value columns
            (rf'{hormone}\s*\([^)]+\)\s*\(Total[^)]*\)\s+\d+\.?\d*\s+(?:ng|µg|ug)/dL\s+(\d+\.?\d*)\s+(?:ng|µg|ug)/dL', 'Table with two value columns (second value)'),
            (rf'{hormone}\s*\([^)]+\)\s*\(Total[^)]*\)\s+(\d+\.?\d*)\s+(?:ng|µg|ug)/dL', 'Table format with /dL'),
            
            # Full name patterns
            (rf'Triiodothyronon.*?(\d+\.?\d*)\s+(?:ng|µg|ug)', 'Triiodothyronon (typo variant)') if hormone == 'T3' else None,
            (rf'Triiodothyronine.*?(\d+\.?\d*)\s+(?:ng|µg|ug)', 'Full name Triiodothyronine') if hormone == 'T3' else None,
            (rf'Tyxorxine.*?(\d+\.?\d*)\s+(?:ng|µg|ug)', 'Tyxorxine (OCR typo)') if hormone == 'T4' else None,
            (rf'Thyroxine.*?(\d+\.?\d*)\s+(?:ng|µg|ug)', 'Full name Thyroxine') if hormone == 'T4' else None,
            
            # Standard patterns
            (rf'{hormone}\s*\([^)]+\)\s*\(Total[^)]*\)\s+(\d+\.?\d*)\s+(?:ng|µg|ug|we)', 'With (Total)'),
            (rf'{hormone}\s*\(Total[^)]*\)\s+(\d+\.?\d*)\s+(?:ng|µg|ug)', 'Total in parentheses'),
            (rf'{hormone}\s+Total\s+(\d+\.?\d*)\s+(?:ng|µg|ug)', 'Total keyword'),
            (rf'{hormone}\s*\([^)]+\)\s+(\d+\.?\d*)\s+(?:ng|µg|ug)', 'With description'),
            (rf'{hormone}\s+(\d+\.?\d*)\s+(?:ng|µg|ug)/dL', 'With /dL'),
            (rf'{hormone}\s*:\s*(\d+\.?\d*)\s+(?:ng|µg|ug)', 'With colon'),
            (rf'{hormone}\s+(\d+\.?\d*)\s+ng', 'Simple with ng'),
            (rf'{hormone}\s+(\d+\.?\d*)\s+µg', 'Simple with µg'),
            (rf'{hormone}\s+(\d+\.?\d*)\s+ug', 'Simple with ug'),
            
            # Loose patterns (last resort)
            (rf'{hormone}[^\d]*(\d+\.?\d*)', 'Very loose pattern'),
        ]
        
        # Filter out None values
        t3_t4_patterns = [p for p in t3_t4_patterns if p is not None]
        
        for pattern, description in t3_t4_patterns:
            print(f"    Trying pattern: {description}")
            table_match = re.search(pattern, text, re.IGNORECASE)
            if table_match:
                try:
                    value = float(table_match.group(1))
                    print(f"      → Matched! Raw value: {value}")
                    
                    # Different valid ranges for different hormones
                    if hormone == 'TSH':
                        valid_range = 0.001 <= value <= 50
                    elif hormone == 'T3':
                        valid_range = 0.1 <= value <= 300  # T3 can be 0.8-2.0 ng/dL or 80-200 ng/dL depending on units
                    elif hormone == 'T4':
                        valid_range = 0.1 <= value <= 25  # T4 typically 5-12 µg/dL
                    else:
                        valid_range = 0.001 <= value <= 50
                    
                    if valid_range:
                        print(f"      ✓ Valid range! Returning {hormone} = {value}")
                        return value
                    else:
                        print(f"      ✗ Out of valid range for {hormone}")
                except (ValueError, IndexError) as e:
                    print(f"      ✗ Error: {e}")
                    continue
            else:
                print(f"      ✗ No match")
        
        # Original table match as fallback
        table_match = re.search(
            rf'{hormone}\s*\([^)]+\)\s*\(Total[^)]*\)\s+(\d+\.?\d*)\s+(?:ng|µg|ug|we)',
            text, re.IGNORECASE
        )
        if table_match:
            try:
                value = float(table_match.group(1))
                if 0.001 <= value <= 50:
                    return value
            except (ValueError, IndexError):
                pass
    
    # Try each pattern
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                value_str = match.group(1)
                # Handle comma as decimal separator
                value_str = value_str.replace(',', '.')
                value = float(value_str)
                
                # Different valid ranges for different hormones
                if hormone == 'TSH':
                    valid_range = 0.001 <= value <= 50
                elif hormone == 'T3':
                    valid_range = 0.1 <= value <= 300
                elif hormone == 'T4':
                    valid_range = 0.1 <= value <= 25
                else:
                    valid_range = 0.001 <= value <= 50
                
                if valid_range:
                    # Additional check: avoid reference ranges (e.g., "0.35-5.50")
                    # Check if this value is part of a range
                    match_pos = match.start()
                    surrounding = text[max(0, match_pos-10):min(len(text), match_pos+50)]
                    
                    # Skip if it looks like a reference range
                    if re.search(rf'{re.escape(value_str)}\s*-\s*\d', surrounding):
                        continue
                    if re.search(rf'\d\s*-\s*{re.escape(value_str)}', surrounding):
                        continue
                    
                    return value
            except (ValueError, IndexError):
                continue
    
    return None

# Symptom-based classification function
def classify_by_symptoms(symptoms_str):
    """
    Classify thyroid condition based on symptoms
    Returns: 'hypothyroid', 'hyperthyroid', 'goiter', or None
    """
    symptoms_lower = symptoms_str.lower()
    
    # Hypothyroid symptoms
    hypothyroid_symptoms = ['fatigue', 'weight_gain', 'cold_sensitivity', 'dry_skin', 'hair_loss', 'muscle_weakness']
    # Hyperthyroid symptoms
    hyperthyroid_symptoms = ['heat_sensitivity', 'irregular_heartbeat', 'mood_swings', 'weight_loss']
    # Goiter symptoms
    goiter_symptoms = ['neck_swelling']
    
    # Count symptom matches
    hypothyroid_count = sum(1 for s in hypothyroid_symptoms if s in symptoms_lower)
    hyperthyroid_count = sum(1 for s in hyperthyroid_symptoms if s in symptoms_lower)
    goiter_count = sum(1 for s in goiter_symptoms if s in symptoms_lower)
    
    # Goiter is most specific
    if goiter_count > 0:
        return 'goiter'
    
    # Compare hypothyroid vs hyperthyroid
    if hypothyroid_count > hyperthyroid_count:
        return 'hypothyroid'
    elif hyperthyroid_count > hypothyroid_count:
        return 'hyperthyroid'
    
    return None

# Updated analyze_thyroid function with Benign/Malignant classification
def analyze_thyroid(tsh, t3, t4, patient_id=None, symptoms=''):
    """
    Analyze thyroid function based on TSH (mandatory) and optional T3, T4 values.
    Returns clear Benign or Malignant classification with detailed analysis.
    
    Medical Guidelines for TSH-based Classification:
    - Normal TSH (0.4-4.0 mIU/L): Generally Benign
    - Abnormal TSH (<0.4 or >4.0 mIU/L): Requires further evaluation
    - Severely abnormal TSH: Higher risk classification
    """
    
    # Get patient info for enhanced analysis
    age = 30  # default
    gender = 0  # default (M)
    
    if patient_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT age, gender FROM patients WHERE patient_id = %s", (patient_id,))
            patient = cursor.fetchone()
            if patient:
                age = patient['age'] or 30
                gender = 1 if patient['gender'] == 'Female' else 0
            cursor.close()
            conn.close()
        except:
            pass
    
    # Classify based on symptoms for additional context
    symptom_classification = classify_by_symptoms(symptoms)
    
    # Updated TSH-based classification with new logic rules
    def get_tsh_classification(tsh_value):
        """
        Classify based on TSH levels with updated medical guidelines:
        
        Rule 1: Normal Case - IF 0.4 ≤ TSH ≤ 4.0 → Benign (Normal thyroid function)
        Rule 2: Mild Abnormality - IF 0.1 ≤ TSH < 0.4 OR 4.0 < TSH ≤ 10 → Benign (Monitor required)
        Rule 3: Severe Abnormality - IF TSH < 0.1 OR TSH > 10 → Malignancy-suspected
        """
        
        # Rule 1: Normal Case
        if 0.4 <= tsh_value <= 4.0:
            return {
                'classification': 'BENIGN',
                'condition': 'Normal Thyroid Function',
                'risk_level': 'LOW',
                'confidence': 95,
                'medical_action': 'Regular monitoring recommended'
            }
        
        # Rule 2: Mild Abnormality (Monitor Required)
        elif (0.1 <= tsh_value < 0.4) or (4.0 < tsh_value <= 10.0):
            if tsh_value < 0.4:
                condition = 'Mild Hyperthyroidism'
                action = 'Monitor thyroid function regularly'
            else:
                condition = 'Mild Hypothyroidism'
                action = 'Monitor and consider treatment if symptoms persist'
            
            return {
                'classification': 'BENIGN (Monitor Required)',
                'condition': condition,
                'risk_level': 'MODERATE',
                'confidence': 90,
                'medical_action': action
            }
        
        # Rule 3: Severe Abnormality (High-Risk)
        else:  # TSH < 0.1 or TSH > 10
            if tsh_value < 0.1:
                condition = 'Severe Hyperthyroidism'
                action = 'URGENT - Immediate endocrinologist consultation required'
            else:  # TSH > 10
                condition = 'Severe Hypothyroidism'
                action = 'URGENT - Immediate medical attention required'
            
            return {
                'classification': 'MALIGNANCY-SUSPECTED',
                'condition': condition,
                'risk_level': 'HIGH',
                'confidence': 93,
                'medical_action': action
            }
    
    # Get primary classification based on TSH
    tsh_analysis = get_tsh_classification(tsh)
    
    # Enhanced analysis with T3 and T4 if available
    additional_info = ""
    if t3 > 0 and t4 > 0:
        # T3 normal range: 0.8-2.0 ng/dL, T4 normal range: 5.0-12.0 µg/dL
        t3_status = "Normal" if 0.8 <= t3 <= 2.0 else ("High" if t3 > 2.0 else "Low")
        t4_status = "Normal" if 5.0 <= t4 <= 12.0 else ("High" if t4 > 12.0 else "Low")
        additional_info = f" | T3: {t3:.2f} ng/dL ({t3_status}) | T4: {t4:.2f} µg/dL ({t4_status})"
        
        # Adjust confidence based on T3/T4 consistency
        if (tsh < 0.4 and (t3_status == "High" or t4_status == "High")) or \
           (tsh > 4.0 and (t3_status == "Low" or t4_status == "Low")):
            tsh_analysis['confidence'] = min(tsh_analysis['confidence'] + 5, 98)
    
    # Consider symptoms for additional information (DO NOT override TSH classification)
    symptom_modifier = ""
    if symptom_classification:
        if symptom_classification == 'goiter':
            # Note goiter but keep TSH-based classification
            symptom_modifier = " | GOITER DETECTED - Neck swelling present (requires additional evaluation)"
        else:
            symptom_modifier = f" | Symptoms suggest: {symptom_classification}"
    
    # Use ML model if available for additional validation
    ml_confidence_boost = 0
    if ML_AVAILABLE:
        try:
            features = np.array([[tsh, t3, t4, age, gender]])
            features_scaled = scaler.transform(features)
            
            prediction = ml_model.predict(features_scaled)[0]
            probabilities = ml_model.predict_proba(features_scaled)[0]
            ml_confidence = float(max(probabilities) * 100)
            
            diagnosis = label_encoder.inverse_transform([prediction])[0]
            
            # Boost confidence if ML agrees with rule-based analysis
            if (diagnosis == 'normal' and tsh_analysis['classification'] == 'BENIGN') or \
               (diagnosis in ['hyperthyroid', 'hypothyroid'] and 'MALIGNANT' in tsh_analysis['classification']):
                ml_confidence_boost = 3
                
        except Exception as e:
            print(f"ML prediction error: {e}")
    
    # Final confidence calculation
    final_confidence = min(tsh_analysis['confidence'] + ml_confidence_boost, 98)
    
    # Generate comprehensive result
    result = f"""
🔬 THYROID ANALYSIS REPORT

📊 CLASSIFICATION: {tsh_analysis['classification']}
🏥 CONDITION: {tsh_analysis['condition']}
⚠️  RISK LEVEL: {tsh_analysis['risk_level']}
📈 CONFIDENCE: {final_confidence}%

📋 DETAILED ANALYSIS:
• TSH Level: {tsh:.3f} mIU/L{additional_info}{symptom_modifier}

🩺 MEDICAL RECOMMENDATION:
{tsh_analysis['medical_action']}

📌 INTERPRETATION:
• TSH is the primary indicator for thyroid function
• Normal range: 0.4-4.0 mIU/L
• Your TSH level indicates: {tsh_analysis['condition']}
• Classification: {tsh_analysis['classification']}
""".strip()
    
    return result, final_confidence

# OCR Extraction Endpoint (for hybrid approach)
@app.route('/api/ocr-extract', methods=['POST'])
def ocr_extract():
    """Extract values from image using OCR without saving to database"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': True, 'message': 'No image provided'}), 400
        
        if not OCR_AVAILABLE:
            return jsonify({'error': True, 'message': 'OCR not available'}), 503
        
        file = request.files['image']
        
        # Save temporarily
        temp_filename = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_filepath)
        
        try:
            # Open and preprocess image for better OCR
            from PIL import ImageEnhance, ImageFilter
            import cv2
            import numpy as np
            
            image = Image.open(temp_filepath)
            
            # AGGRESSIVE preprocessing for decimal point detection
            # 1. Convert to grayscale
            image = image.convert('L')
            
            # 2. Resize to very large size for better decimal point detection
            width, height = image.size
            scale_factor = 2000 / width  # Scale to 2000px width
            new_size = (int(width * scale_factor), int(height * scale_factor))
            image = image.resize(new_size, Image.LANCZOS)
            
            # 3. Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # 4. Apply bilateral filter to reduce noise while keeping edges
            img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
            
            # 5. Apply adaptive thresholding for better text/background separation
            img_array = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 6. Morphological operations to enhance text
            kernel = np.ones((1, 1), np.uint8)
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            image = Image.fromarray(img_array)
            
            # 7. Enhance contrast aggressively
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(3.0)
            
            # 8. Enhance sharpness aggressively
            sharpener = ImageEnhance.Sharpness(image)
            image = sharpener.enhance(3.0)
            
            # 9. Apply unsharp mask for even better sharpness
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
            # Extract text with multiple configs for better accuracy
            configs = [
                r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.',  # Only digits and decimal
                r'--oem 3 --psm 6',  # Assume uniform block of text
                r'--oem 3 --psm 4',  # Assume single column of text
                r'--oem 3 --psm 3',  # Fully automatic page segmentation
                r'--oem 1 --psm 6',  # Use LSTM OCR engine
            ]
            
            text = ""
            for config in configs:
                try:
                    extracted = pytesseract.image_to_string(image, config=config)
                    if len(extracted) > len(text):
                        text = extracted
                except:
                    continue
            
            print(f"\n{'='*60}")
            print(f"OCR EXTRACTED TEXT:")
            print(f"{'='*60}")
            print(text)
            print(f"{'='*60}\n")
            
            # Extract values with detailed logging
            print("Attempting to extract TSH...")
            tsh_value = extract_value(text, 'TSH')
            print(f"  → TSH Result: {tsh_value}")
            
            print("Attempting to extract T3...")
            t3_value = extract_value(text, 'T3')
            print(f"  → T3 Result: {t3_value}")
            
            print("Attempting to extract T4...")
            t4_value = extract_value(text, 'T4')
            print(f"  → T4 Result: {t4_value}")
            
            print(f"\nFINAL EXTRACTED VALUES:")
            print(f"  TSH: {tsh_value}")
            print(f"  T3:  {t3_value}")
            print(f"  T4:  {t4_value}")
            print(f"{'='*60}\n")
            
            # Clean up temp file
            try:
                os.remove(temp_filepath)
            except:
                pass
            
            # Return extracted values (keep None if not found, don't convert to 0)
            return jsonify({
                'tsh_value': tsh_value,
                't3_value': t3_value,  # Return actual value or None
                't4_value': t4_value,  # Return actual value or None
                'success': True
            })
            
        except Exception as e:
            print(f"OCR Error: {str(e)}")  # Debug logging
            # Clean up temp file
            try:
                os.remove(temp_filepath)
            except:
                pass
            return jsonify({'error': True, 'message': f'Error processing image: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': True, 'message': str(e)}), 500

# Thyroid Check with OCR or Manual Input
@app.route('/api/thyroid-check', methods=['POST'])
def thyroid_check():
    try:
        patient_id = request.form.get('patient_id')
        symptoms = request.form.get('symptoms', '')
        
        # Check if manual values provided
        manual_tsh = request.form.get('tsh_manual', '').strip()
        manual_t3 = request.form.get('t3_manual', '').strip()
        manual_t4 = request.form.get('t4_manual', '').strip()
        
        print(f"Received manual values - TSH: '{manual_tsh}', T3: '{manual_t3}', T4: '{manual_t4}'")  # Debug
        
        if manual_tsh:  # If TSH is provided
            # Manual input mode
            try:
                tsh_value = float(manual_tsh)
                t3_value = float(manual_t3) if manual_t3 else 0
                t4_value = float(manual_t4) if manual_t4 else 0
                filepath = None
                print(f"Parsed manual values - TSH: {tsh_value}, T3: {t3_value}, T4: {t4_value}")  # Debug
            except ValueError as e:
                return jsonify({'error': True, 'message': f'Invalid number format: {str(e)}'}), 400
        elif 'image' in request.files and OCR_AVAILABLE:
            # OCR mode
            file = request.files['image']
            filename = f"{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                # Open and preprocess image for better OCR
                from PIL import ImageEnhance, ImageFilter
                import cv2
                import numpy as np
                
                image = Image.open(filepath)
                
                # AGGRESSIVE preprocessing for decimal point detection
                # 1. Convert to grayscale
                image = image.convert('L')
                
                # 2. Resize to very large size for better decimal point detection
                width, height = image.size
                scale_factor = 2000 / width  # Scale to 2000px width (was 1000)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.LANCZOS)
                
                # 3. Convert to numpy array for OpenCV processing
                img_array = np.array(image)
                
                # 4. Apply bilateral filter to reduce noise while keeping edges
                img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
                
                # 5. Apply adaptive thresholding for better text/background separation
                img_array = cv2.adaptiveThreshold(
                    img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                
                # 6. Morphological operations to enhance text
                kernel = np.ones((1, 1), np.uint8)
                img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
                
                # Convert back to PIL Image
                image = Image.fromarray(img_array)
                
                # 7. Enhance contrast aggressively
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(3.0)  # Increased from 2.0 to 3.0
                
                # 8. Enhance sharpness aggressively
                sharpener = ImageEnhance.Sharpness(image)
                image = sharpener.enhance(3.0)  # Increased from 2.0 to 3.0
                
                # 9. Apply unsharp mask for even better sharpness
                image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
                
                # Extract text with multiple configs for better accuracy
                configs = [
                    r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.',  # Only digits and decimal
                    r'--oem 3 --psm 6',  # Assume uniform block of text
                    r'--oem 3 --psm 4',  # Assume single column of text
                    r'--oem 3 --psm 3',  # Fully automatic page segmentation
                    r'--oem 1 --psm 6',  # Use LSTM OCR engine
                ]
                
                text = ""
                for config in configs:
                    try:
                        extracted = pytesseract.image_to_string(image, config=config)
                        if len(extracted) > len(text):
                            text = extracted
                    except:
                        continue
                
                print(f"OCR Extracted Text:\n{text}\n")  # Debug logging
                
                # Extract values
                tsh_value = extract_value(text, 'TSH')
                t3_value = extract_value(text, 'T3')
                t4_value = extract_value(text, 'T4')
                
                print(f"Extracted values - TSH: {tsh_value}, T3: {t3_value}, T4: {t4_value}")  # Debug
                
                # Set defaults for missing values
                if t3_value is None:
                    t3_value = 0
                if t4_value is None:
                    t4_value = 0
                    
            except Exception as e:
                print(f"OCR Error: {str(e)}")  # Debug logging
                return jsonify({'error': True, 'message': f'Error processing image: {str(e)}'}), 500
        else:
            return jsonify({'error': True, 'message': 'Please provide either image or manual values'}), 400
    
        if tsh_value is None:
            result = 'No TSH value in the report. For further assessment, please consult a doctor.'
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO thyroid_reports (patient_id, test_result, symptoms, image_path) 
                            VALUES (%s, %s, %s, %s)""", (patient_id, result, symptoms, filepath))
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'error': True, 'message': result}), 200
        
        # If T3 and T4 are not provided, set to 0
        if t3_value is None:
            t3_value = 0
        if t4_value is None:
            t4_value = 0
        
        # Analyze results with confidence score and symptoms
        result, confidence = analyze_thyroid(tsh_value, t3_value, t4_value, patient_id, symptoms)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """INSERT INTO thyroid_reports (patient_id, tsh_value, t3_value, t4_value, 
                   test_result, symptoms, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (patient_id, tsh_value, t3_value, t4_value, result, symptoms, filepath))
        report_id = cursor.lastrowid
        conn.commit()
        
        # Send thyroid report email
        if EMAIL_ENABLED:
            try:
                cursor2 = conn.cursor(dictionary=True)
                cursor2.execute("SELECT full_name, email FROM patients WHERE patient_id = %s", (patient_id,))
                patient = cursor2.fetchone()
                cursor2.close()
                if patient:
                    report_data = {
                        'tsh_value': tsh_value,
                        't3_value': t3_value,
                        't4_value': t4_value,
                        'result': result,
                        'confidence': confidence
                    }
                    send_thyroid_report_email(patient['full_name'], patient['email'], report_data)
            except Exception as e:
                print(f"Email sending failed: {e}")
        
        cursor.close()
        conn.close()
    
        return jsonify({
            'tsh_value': round(tsh_value, 3),  # Ensure 3 decimal places
            't3_value': round(t3_value, 3),
            't4_value': round(t4_value, 3),
            'result': result,
            'confidence': confidence
        }), 200
    
    except Exception as e:
        print(f"Thyroid check error: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()
        return jsonify({'error': True, 'message': f'Error: {str(e)}'}), 500

# Get Patient Reports
@app.route('/api/reports/<int:patient_id>', methods=['GET'])
def get_reports(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM thyroid_reports WHERE patient_id = %s ORDER BY report_date DESC", 
                      (patient_id,))
        reports = cursor.fetchall()
        
        for report in reports:
            report['report_date'] = str(report['report_date'])
        
        return jsonify(reports), 200
    finally:
        cursor.close()
        conn.close()

# Download Report Image (uploaded image only)
@app.route('/api/reports/download/<int:report_id>', methods=['GET'])
def download_report(report_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM thyroid_reports WHERE report_id = %s", (report_id,))
        report = cursor.fetchone()
        
        if not report:
            return jsonify({'message': 'Report not found'}), 404
        
        if not report['image_path']:
            return jsonify({'message': 'No image was uploaded for this report (manual entry)'}), 404
        
        # Check if file exists, handle both relative and absolute paths
        image_path = report['image_path']
        if not os.path.isabs(image_path):
            # If relative path, make it relative to backend directory
            image_path = os.path.join(os.path.dirname(__file__), image_path)
        
        if os.path.exists(image_path):
            return send_file(image_path, as_attachment=True)
        else:
            return jsonify({'message': 'Image file not found on server. It may have been deleted.'}), 404
    except Exception as e:
        return jsonify({'message': f'Error downloading image: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# Get Patient Profile
@app.route('/api/patient/profile/<int:patient_id>', methods=['GET'])
def get_patient_profile(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT patient_id, full_name, email, phone, age, gender, address, created_at FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            patient['created_at'] = str(patient['created_at'])
            return jsonify(patient), 200
        else:
            return jsonify({'message': 'Patient not found'}), 404
    finally:
        cursor.close()
        conn.close()

# Update Patient Profile (only phone and address allowed)
@app.route('/api/patient/profile/<int:patient_id>', methods=['PUT'])
def update_patient_profile(patient_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Only allow updating phone and address
        query = """UPDATE patients SET phone = %s, address = %s WHERE patient_id = %s"""
        values = (data.get('phone', ''), data.get('address', ''), patient_id)
        
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({'message': 'Contact information updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ═══════════════════════════════════════════════════════════════════
# DOCTOR MODULE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

# Doctor Registration
@app.route('/api/doctor/register', methods=['POST'])
def register_doctor():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = generate_password_hash(data['password'])
        
        query = """INSERT INTO doctors (full_name, email, password, phone, specialization, 
                   available_days)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (data['full_name'], data['email'], hashed_password, 
                  data['phone'], data['specialization'], data['available_days'])
        
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({'message': 'Doctor registration successful'}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'message': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Doctor Login
@app.route('/api/doctor/login', methods=['POST'])
def login_doctor():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM doctors WHERE email = %s", (data['email'],))
        doctor = cursor.fetchone()
        
        if doctor and check_password_hash(doctor['password'], data['password']):
            return jsonify({
                'doctor_id': doctor['doctor_id'],
                'full_name': doctor['full_name'],
                'email': doctor['email'],
                'specialization': doctor['specialization'],
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    finally:
        cursor.close()
        conn.close()

# Get Doctor's Appointments
@app.route('/api/doctor/appointments/<int:doctor_id>', methods=['GET'])
def get_doctor_appointments(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """SELECT a.*, p.full_name as patient_name, p.email as patient_email, 
                   p.phone as patient_phone
                   FROM appointments a 
                   JOIN patients p ON a.patient_id = p.patient_id 
                   WHERE a.doctor_id = %s 
                   ORDER BY a.appointment_date DESC, a.appointment_time DESC"""
        cursor.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        
        # Convert date and time to string
        for apt in appointments:
            apt['appointment_date'] = str(apt['appointment_date'])
            apt['appointment_time'] = str(apt['appointment_time'])
        
        return jsonify(appointments), 200
    finally:
        cursor.close()
        conn.close()

# Update Appointment Status
@app.route('/api/doctor/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ['Pending', 'Confirmed', 'Completed', 'Cancelled']:
        return jsonify({'message': 'Invalid status'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE appointments SET status = %s WHERE appointment_id = %s", 
                      (new_status, appointment_id))
        conn.commit()
        
        # Send email notification if enabled
        if EMAIL_ENABLED and new_status == 'Confirmed':
            try:
                cursor2 = conn.cursor(dictionary=True)
                cursor2.execute("""
                    SELECT p.full_name, p.email, d.full_name as doctor_name, 
                           a.appointment_date
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
                    JOIN doctors d ON a.doctor_id = d.doctor_id
                    WHERE a.appointment_id = %s
                """, (appointment_id,))
                apt_info = cursor2.fetchone()
                cursor2.close()
                
                if apt_info:
                    send_appointment_status_email(
                        apt_info['full_name'],
                        apt_info['email'],
                        apt_info['doctor_name'],
                        str(apt_info['appointment_date']),
                        new_status
                    )
            except Exception as e:
                print(f"Email sending failed: {e}")
        
        return jsonify({'message': 'Appointment status updated'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Get Patient Reports for Doctor's Appointments
@app.route('/api/doctor/patient-reports/<int:doctor_id>', methods=['GET'])
def get_patient_reports_for_doctor(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """SELECT DISTINCT r.*, p.full_name as patient_name, p.email as patient_email
                   FROM thyroid_reports r
                   JOIN patients p ON r.patient_id = p.patient_id
                   WHERE r.patient_id IN (
                       SELECT DISTINCT patient_id 
                       FROM appointments 
                       WHERE doctor_id = %s
                   )
                   ORDER BY r.report_date DESC"""
        cursor.execute(query, (doctor_id,))
        reports = cursor.fetchall()
        
        for report in reports:
            report['report_date'] = str(report['report_date'])
        
        return jsonify(reports), 200
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)


# Test route
@app.route('/api/test', methods=['GET', 'POST'])
def test_route():
    return jsonify({'message': 'Test route works!'}), 200
# Password Reset System
import random
import string
from datetime import datetime, timedelta

# Store reset codes temporarily (in production, use Redis or database)
reset_codes = {}

def generate_reset_code():
    """Generate a 6-digit reset code"""
    return ''.join(random.choices(string.digits, k=6))

def send_reset_email(email, code, user_type):
    """Send password reset email"""
    if not EMAIL_ENABLED:
        print(f"Email disabled. Reset code for {email}: {code}")
        return True
    
    try:
        subject = f"Password Reset Code - ThyroDetect {user_type.title()} Portal"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code-box {{ background: white; border: 2px dashed #667eea; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                    <p>ThyroDetect {user_type.title()} Portal</p>
                </div>
                <div class="content">
                    <h2>Hello,</h2>
                    <p>We received a request to reset your password for your ThyroDetect {user_type} account.</p>
                    
                    <div class="code-box">
                        <p>Your verification code is:</p>
                        <div class="code">{code}</div>
                        <p><small>This code expires in 15 minutes</small></p>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This code is valid for 15 minutes only</li>
                            <li>Never share this code with anyone</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>If you have any questions, please contact our support team.</p>
                    
                    <p>Best regards,<br>ThyroDetect Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_email(email, subject, html_body)
        return True
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        return False

# Patient Password Reset - Request Code
@app.route('/api/patient/forgot-password', methods=['POST'])
def patient_forgot_password():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if patient exists
        cursor.execute("SELECT patient_id, full_name FROM patients WHERE email = %s", (email,))
        patient = cursor.fetchone()
        
        if not patient:
            return jsonify({'message': 'If this email exists in our system, you will receive a reset code shortly.'}), 200
        
        # Generate reset code
        code = generate_reset_code()
        expiry = datetime.now() + timedelta(minutes=15)
        
        # Store reset code
        reset_codes[email] = {
            'code': code,
            'expiry': expiry,
            'user_type': 'patient',
            'user_id': patient[0]
        }
        
        # Send email
        if send_reset_email(email, code, 'patient'):
            return jsonify({'message': 'Reset code sent to your email'}), 200
        else:
            return jsonify({'message': 'Failed to send reset email'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Verify Reset Code (Both Patient and Doctor)
@app.route('/api/verify-reset-code', methods=['POST'])
def verify_reset_code():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    
    if not email or not code:
        return jsonify({'message': 'Email and code are required'}), 400
    
    # Check if code exists and is valid
    if email not in reset_codes:
        return jsonify({'message': 'Invalid or expired reset code'}), 400
    
    stored_data = reset_codes[email]
    
    # Check if code matches and hasn't expired
    if stored_data['code'] != code:
        return jsonify({'message': 'Invalid reset code'}), 400
    
    if datetime.now() > stored_data['expiry']:
        del reset_codes[email]
        return jsonify({'message': 'Reset code has expired'}), 400
    
    # Mark code as verified
    reset_codes[email]['verified'] = True
    
    return jsonify({
        'message': 'Code verified successfully',
        'user_type': stored_data['user_type']
    }), 200



# Resend Reset Code
@app.route('/api/resend-reset-code', methods=['POST'])
def resend_reset_code():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    # Check if there's an existing reset session
    if email not in reset_codes:
        return jsonify({'message': 'No active reset session found'}), 400
    
    stored_data = reset_codes[email]
    
    # Generate new code
    code = generate_reset_code()
    expiry = datetime.now() + timedelta(minutes=15)
    
    # Update stored data
    reset_codes[email].update({
        'code': code,
        'expiry': expiry,
        'verified': False
    })
    
    # Send new email
    if send_reset_email(email, code, stored_data['user_type']):
        return jsonify({'message': 'New reset code sent to your email'}), 200
    else:
        return jsonify({'message': 'Failed to send reset email'}), 500