-- Thyroid Cancer Detection Database Schema

CREATE DATABASE IF NOT EXISTS thyroid_detection;
USE thyroid_detection;
-- Patients Table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    address TEXT,
    security_question_1 VARCHAR(255),
    security_answer_1 VARCHAR(255),
    security_question_2 VARCHAR(255),
    security_answer_2 VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
select *from doctors;
-- Doctors Table
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    available_days VARCHAR(100),
    security_question_1 VARCHAR(255),
    security_answer_1 VARCHAR(255),
    security_question_2 VARCHAR(255),
    security_answer_2 VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments Table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- Health Checkup Records
CREATE TABLE IF NOT EXISTS health_checkups (
    checkup_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    sleep_hours DECIMAL(3,1),
    working_hours DECIMAL(3,1),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    water_intake DECIMAL(4,2),
    health_tip TEXT,
    checkup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Thyroid Test Reports
CREATE TABLE IF NOT EXISTS thyroid_reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    tsh_value DECIMAL(6,3),
    t3_value DECIMAL(6,3) DEFAULT 0,
    t4_value DECIMAL(6,3) DEFAULT 0,
    test_result VARCHAR(100),
    symptoms TEXT,
    image_path VARCHAR(255),
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Insert Sample Doctors
-- NOTE: Passwords are stored as plain text here for initial setup
-- The setup_database.py script will hash these passwords properly
-- Default password for all doctors: Doctor@123
INSERT INTO doctors (full_name, email, password, specialization, phone, available_days) VALUES
('Dr. Sarah Johnson', 'sarah.johnson@hospital.com', 'Doctor@123', 'Endocrinologist', '555-0101', 'Mon, Wed, Fri'),
('Dr. Michael Chen', 'michael.chen@hospital.com', 'Doctor@123', 'Oncologist', '555-0102', 'Tue, Thu, Sat'),
('Dr. Emily Rodriguez', 'emily.rodriguez@hospital.com', 'Doctor@123', 'General Physician', '555-0103', 'Mon, Tue, Wed, Thu, Fri'),
('Dr. James Wilson', 'james.wilson@hospital.com', 'Doctor@123', 'Endocrinologist', '555-0104', 'Wed, Thu, Fri, Sat');
