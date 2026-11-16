import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import os

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'pruthvimy666@gmail.com',
    'sender_password': 'evtj fpfb gzyl jzqa',
    'sender_name': 'Thyroid Care System'
}

def send_email(to_email, subject, html_content, attachment_path=None):
    """Send email with optional attachment"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='pdf')
                attachment.add_header('Content-Disposition', 'attachment', 
                                    filename=os.path.basename(attachment_path))
                msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_registration_email(patient_name, patient_email):
    """Send welcome email after registration"""
    subject = "Welcome to the Thyroid Health App!"
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome!</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0d6efd; color: #ffffff; padding: 20px 30px;">
                <h1 style="margin: 0; font-size: 24px;">Welcome to the Thyroid Health App!</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="font-size: 20px; color: #333;">Hello, {patient_name}!</h2>
                <p style="color: #555; font-size: 16px;">We are excited to have you join our community. You can now log in to your account to track your health, book appointments, and connect with specialists.</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="http://127.0.0.1:5000/patient/login.html" style="background-color: #0d6efd; color: #ffffff; text-decoration: none; padding: 12px 25px; border-radius: 5px; font-weight: bold; font-size: 16px; display: inline-block;">Login to Your Account</a>
                </p>
                <p style="color: #555; font-size: 16px;">If you have any questions, please don't hesitate to reach out.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 14px; color: #888;">Best regards,<br>The Thyroid Health Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(patient_email, subject, html_content)

def send_login_notification(patient_name, patient_email):
    """Send notification email after login"""
    subject = "Login Notification - Thyroid Care System"
    login_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #667eea;">Login Notification</h2>
            <p>Dear {patient_name},</p>
            <p>Your account was accessed on <strong>{login_time}</strong>.</p>
            
            <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4caf50;">
                <p style="margin: 0;">✓ If this was you, no action is needed.</p>
            </div>
            
            <div style="background: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ff9800;">
                <p style="margin: 0;">⚠ If you did not login, please contact us immediately.</p>
            </div>
            
            <p style="margin-top: 30px;">
                Best regards,<br>
                <strong>Thyroid Care Team</strong>
            </p>
        </div>
    </body>
    </html>
    """
    return send_email(patient_email, subject, html_content)

def send_health_checkup_email(patient_name, patient_email, checkup_data):
    """Send health checkup report via email"""
    subject = "Your Health Checkup Report - Thyroid Care System"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #667eea;">Health Checkup Report</h2>
            <p>Dear {patient_name},</p>
            <p>Here are your health checkup results:</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #f5f7fa;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Parameter</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Value</th>
                </tr>
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">Sleep Hours</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{checkup_data.get('sleep_hours', 'N/A')} hours</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 12px; border: 1px solid #ddd;">Stress Level</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{checkup_data.get('stress_level', 'N/A')}/10</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">Height</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{checkup_data.get('height', 'N/A')} cm</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 12px; border: 1px solid #ddd;">Weight</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{checkup_data.get('weight', 'N/A')} kg</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">Water Intake</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{checkup_data.get('water_intake', 'N/A')} L/day</td>
                </tr>
            </table>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #1976d2; margin-top: 0;">Health Tips:</h3>
                <p>{checkup_data.get('health_tip', 'Keep maintaining a healthy lifestyle!')}</p>
            </div>
            
            <p>Login to your dashboard to view detailed analysis.</p>
            
            <p style="margin-top: 30px;">
                Best regards,<br>
                <strong>Thyroid Care Team</strong>
            </p>
        </div>
    </body>
    </html>
    """
    return send_email(patient_email, subject, html_content)

def send_thyroid_report_email(patient_name, patient_email, report_data, pdf_path=None):
    """Send thyroid test report via email with PDF attachment"""
    subject = "Thyroid Prediction Results"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Prediction Results</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0d6efd; color: #ffffff; padding: 20px 30px;">
                <h1 style="margin: 0; font-size: 24px;">Thyroid Prediction Results</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="font-size: 20px; color: #333;">Hello, {patient_name}</h2>
                <p style="color: #555; font-size: 16px;">Your doctor has completed a new thyroid health prediction based on your recent data.</p>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333;">Prediction Details:</h3>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>TSH:</strong> {report_data.get('tsh_value', 'N/A')}</p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>T3:</strong> {report_data.get('t3_value', 'N/A')}</p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>T4:</strong> {report_data.get('t4_value', 'N/A')}</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="margin: 5px 0; font-size: 16px;"><strong>Prediction Result:</strong> <span style="font-weight: bold; color: #dc3545;">{report_data.get('result', 'Analysis complete')}</span></p>
                </div>
                <p style="color: #555; font-size: 16px; font-weight: bold;">Please note: This is an AI-assisted prediction and not a formal diagnosis. Your doctor will discuss these results and the next steps with you.</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="http://127.0.0.1:5000/patient/dashboard.html" style="background-color: #198754; color: #ffffff; text-decoration: none; padding: 12px 25px; border-radius: 5px; font-weight: bold; font-size: 16px; display: inline-block;">View in Your Dashboard</a>
                </p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 14px; color: #888;">Best regards,<br>The Thyroid Health Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(patient_email, subject, html_content, pdf_path)

def send_appointment_booking_email(patient_name, patient_email, doctor_name, appointment_date, status):
    """Send appointment booking confirmation email"""
    subject = "Appointment Request Received"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appointment Confirmation</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0d6efd; color: #ffffff; padding: 20px 30px;">
                <h1 style="margin: 0; font-size: 24px;">Appointment Request Received</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="font-size: 20px; color: #333;">Your Appointment is Pending</h2>
                <p style="color: #555; font-size: 16px;">Hello, you have successfully requested an appointment. Your doctor will review the request and either approve or reject it shortly.</p>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333;">Appointment Details:</h3>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>Doctor:</strong> Dr. {doctor_name}</p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>Date:</strong> {appointment_date}</p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>Status:</strong> <span style="color: #ffc107; background-color: #fff3cd; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{status}</span></p>
                </div>
                <p style="color: #555; font-size: 16px;">You will receive another email as soon as the status is updated.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 14px; color: #888;">Best regards,<br>The Thyroid Health Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(patient_email, subject, html_content)

def send_appointment_status_email(patient_name, patient_email, doctor_name, appointment_date, status):
    """Send appointment status update email (Approved/Rejected)"""
    subject = "Appointment Status Updated"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appointment Status Updated</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden;">
            {'<div style="background-color: #198754; color: #ffffff; padding: 20px 30px;"><h1 style="margin: 0; font-size: 24px;">Appointment Approved!</h1></div>' if status == 'Approved' else '<div style="background-color: #dc3545; color: #ffffff; padding: 20px 30px;"><h1 style="margin: 0; font-size: 24px;">Appointment Rejected</h1></div>'}
            <div style="padding: 30px;">
                <h2 style="font-size: 20px; color: #333;">Hello, {patient_name}</h2>
                <p style="color: #555; font-size: 16px;">The status of your appointment with <strong>Dr. {doctor_name}</strong> on {appointment_date} has been updated.</p>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                    <h3 style="margin-top: 0; color: #333;">New Status:</h3>
                    {'<span style="color: #198754; background-color: #d1e7dd; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 18px;">' + status + '</span>' if status == 'Approved' else '<span style="color: #dc3545; background-color: #f8d7da; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 18px;">' + status + '</span>'}
                </div>
                {'<p style="color: #555; font-size: 16px;">Your appointment is confirmed. We look forward to seeing you!</p>' if status == 'Approved' else '<p style="color: #555; font-size: 16px;">Unfortunately, your appointment could not be confirmed. Please log in to your dashboard to book a new time or contact the clinic directly.</p>'}
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 14px; color: #888;">Best regards,<br>The Thyroid Health Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(patient_email, subject, html_content)

# Test function
if __name__ == "__main__":
    print("Email Service Module")
    print("Update EMAIL_CONFIG with your SMTP settings before using.")
