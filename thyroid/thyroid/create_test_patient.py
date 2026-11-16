import mysql.connector
from werkzeug.security import generate_password_hash

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Panda@2003',
    database='thyroid_detection'
)
cursor = conn.cursor()

try:
    # Check if test patient already exists
    cursor.execute("SELECT email FROM patients WHERE email = %s", ('test@example.com',))
    if cursor.fetchone():
        print("Test patient already exists!")
    else:
        # Create test patient with security questions
        hashed_password = generate_password_hash('test123')
        
        query = """INSERT INTO patients (full_name, email, password, phone, age, gender, address, 
                   security_question_1, security_answer_1, security_question_2, security_answer_2)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = ('Test Patient', 'test@example.com', hashed_password, 
                  '555-0123', 25, 'Male', '123 Test Street',
                  'What is your favorite fruit?', 'apple',
                  'What school did you study in?', 'government school')
        
        cursor.execute(query, values)
        conn.commit()
        print("✓ Test patient created successfully!")
        print("Email: test@example.com")
        print("Password: test123")
        print("Security Answer 1: apple")
        print("Security Answer 2: government school")

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()