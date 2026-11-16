import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Panda@2003',
    database='thyroid_detection'
)
cursor = conn.cursor(dictionary=True)

try:
    # Check test patient details
    cursor.execute("""
        SELECT patient_id, email, security_question_1, security_answer_1, 
               security_question_2, security_answer_2 
        FROM patients 
        WHERE email = 'test@example.com'
    """)
    patient = cursor.fetchone()
    
    if patient:
        print("Test Patient Found:")
        print(f"Patient ID: {patient['patient_id']}")
        print(f"Email: {patient['email']}")
        print(f"Security Question 1: '{patient['security_question_1']}'")
        print(f"Security Answer 1: '{patient['security_answer_1']}'")
        print(f"Security Question 2: '{patient['security_question_2']}'")
        print(f"Security Answer 2: '{patient['security_answer_2']}'")
    else:
        print("Test patient not found!")
        
    # Check if security columns exist
    cursor.execute("SHOW COLUMNS FROM patients LIKE 'security_%'")
    columns = cursor.fetchall()
    print(f"\nSecurity columns in patients table: {len(columns)}")
    for col in columns:
        print(f"- {col['Field']}")

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()