import mysql.connector
import sys
from werkzeug.security import generate_password_hash

print("Setting up Thyroid Detection Database...")
print("=" * 50)

DB_PASSWORD = "Panda@2003"

try:
    # Connect to MySQL server
    print("Connecting to MySQL server...")
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("✓ Connected to MySQL")
    
    # Create database
    print("\nCreating database...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS thyroid_detection")
    cursor.execute("USE thyroid_detection")
    print("✓ Database 'thyroid_detection' created/selected")
    
    # Create patients table
    print("\nCreating tables...")
    cursor.execute("""
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    print("✓ Patients table created")
    
    # Create doctors table
    cursor.execute("""
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
        )
    """)
    print("✓ Doctors table created")
    
    # Create appointments table
    cursor.execute("""
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
        )
    """)
    print("✓ Appointments table created")
    
    # Create health_checkups table
    cursor.execute("""
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
        )
    """)
    print("✓ Health checkups table created")
    
    # Create thyroid_reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS thyroid_reports (
            report_id INT PRIMARY KEY AUTO_INCREMENT,
            patient_id INT NOT NULL,
            tsh_value DECIMAL(6,3),
            t3_value DECIMAL(6,3) DEFAULT 0,
            t4_value DECIMAL(6,3) DEFAULT 0,
            test_result TEXT,
            symptoms TEXT,
            image_path VARCHAR(255),
            report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
        )
    """)
    print("✓ Thyroid reports table created")
    
    # Check if security question columns exist in doctors table
    print("\nChecking doctors table structure...")
    cursor.execute("SHOW COLUMNS FROM doctors LIKE 'security_question_1'")
    security_columns_exist = cursor.fetchone() is not None
    
    if not security_columns_exist:
        print("Adding security question columns to doctors table...")
        cursor.execute("ALTER TABLE doctors ADD COLUMN security_question_1 VARCHAR(255)")
        cursor.execute("ALTER TABLE doctors ADD COLUMN security_answer_1 VARCHAR(255)")
        cursor.execute("ALTER TABLE doctors ADD COLUMN security_question_2 VARCHAR(255)")
        cursor.execute("ALTER TABLE doctors ADD COLUMN security_answer_2 VARCHAR(255)")
        conn.commit()
        print("✓ Security question columns added to doctors table")
    
    # Check if security question columns exist in patients table
    print("\nChecking patients table structure...")
    cursor.execute("SHOW COLUMNS FROM patients LIKE 'security_question_1'")
    patient_security_columns_exist = cursor.fetchone() is not None
    
    if not patient_security_columns_exist:
        print("Adding security question columns to patients table...")
        cursor.execute("ALTER TABLE patients ADD COLUMN security_question_1 VARCHAR(255)")
        cursor.execute("ALTER TABLE patients ADD COLUMN security_answer_1 VARCHAR(255)")
        cursor.execute("ALTER TABLE patients ADD COLUMN security_question_2 VARCHAR(255)")
        cursor.execute("ALTER TABLE patients ADD COLUMN security_answer_2 VARCHAR(255)")
        conn.commit()
        print("✓ Security question columns added to patients table")
    
    # Check if password column exists in doctors table
    cursor.execute("SHOW COLUMNS FROM doctors LIKE 'password'")
    password_column_exists = cursor.fetchone() is not None
    
    if not password_column_exists:
        print("Adding password column to doctors table...")
        cursor.execute("ALTER TABLE doctors ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT ''")
        conn.commit()
        print("✓ Password column added to doctors table")
    
    # Insert sample doctors
    print("\nInserting sample doctors...")
    cursor.execute("SELECT COUNT(*) FROM doctors")
    count = cursor.fetchone()[0]
    
    if count == 0:
        doctors = [
            ('Dr. Sarah Johnson', 'sarah.johnson@hospital.com', 'Doctor@123', 'Endocrinologist', '555-0101', 'Mon, Wed, Fri'),
            ('Dr. Michael Chen', 'michael.chen@hospital.com', 'Doctor@123', 'Oncologist', '555-0102', 'Tue, Thu, Sat'),
            ('Dr. Emily Rodriguez', 'emily.rodriguez@hospital.com', 'Doctor@123', 'General Physician', '555-0103', 'Mon, Tue, Wed, Thu, Fri'),
            ('Dr. James Wilson', 'james.wilson@hospital.com', 'Doctor@123', 'Endocrinologist', '555-0104', 'Wed, Thu, Fri, Sat')
        ]
        
        for doctor in doctors:
            # Hash the password
            hashed_password = generate_password_hash(doctor[2])
            cursor.execute("""
                INSERT INTO doctors (full_name, email, password, specialization, phone, available_days,
                                   security_question_1, security_answer_1, security_question_2, security_answer_2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (doctor[0], doctor[1], hashed_password, doctor[3], doctor[4], doctor[5],
                  'What is your favorite fruit?', 'apple',
                  'What type of school did you attend for primary education?', 'government school'))
        
        conn.commit()
        print(f"✓ Inserted {len(doctors)} sample doctors with security questions")
    else:
        # Check if existing doctors have passwords
        cursor.execute("SELECT COUNT(*) FROM doctors WHERE password = '' OR password IS NULL")
        doctors_without_passwords = cursor.fetchone()[0]
        
        if doctors_without_passwords > 0:
            print(f"Updating passwords for {doctors_without_passwords} existing doctors...")
            # Update existing doctors with default password
            hashed_password = generate_password_hash('Doctor@123')
            cursor.execute("UPDATE doctors SET password = %s WHERE password = '' OR password IS NULL", (hashed_password,))
            conn.commit()
            print("✓ Updated passwords for existing doctors")
        
        # Check if existing doctors have security questions
        cursor.execute("SELECT COUNT(*) FROM doctors WHERE security_question_1 IS NULL OR security_question_1 = ''")
        doctors_without_security = cursor.fetchone()[0]
        
        if doctors_without_security > 0:
            print(f"Adding security questions for {doctors_without_security} existing doctors...")
            cursor.execute("""
                UPDATE doctors 
                SET security_question_1 = %s, security_answer_1 = %s,
                    security_question_2 = %s, security_answer_2 = %s
                WHERE security_question_1 IS NULL OR security_question_1 = ''
            """, ('What is your favorite fruit?', 'apple',
                  'What type of school did you attend for primary education?', 'government school'))
            conn.commit()
            print("✓ Added security questions for existing doctors")
        
        print(f"✓ Doctors already exist ({count} doctors)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✓ Database setup completed successfully!")
    print("\nYou can now:")
    print("1. Run: python test_backend.py")
    print("2. Or open: frontend/index.html")
    
except mysql.connector.Error as err:
    print(f"\n✗ MySQL Error: {err}")
    print("\nPlease check:")
    print("1. MySQL service is running")
    print("2. Password is correct: Panda@2003")
    print("3. MySQL is installed properly")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
