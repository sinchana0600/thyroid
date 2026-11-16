import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Panda@2003',
    database='thyroid_detection'
)
cursor = conn.cursor()

try:
    # Update test patient to remove trailing spaces and ensure correct answers
    cursor.execute("""
        UPDATE patients 
        SET security_answer_1 = 'apple', 
            security_answer_2 = 'government school'
        WHERE email = 'test@example.com'
    """)
    conn.commit()
    print("✓ Test patient security answers updated (removed trailing spaces)")
    
    # Verify the update
    cursor.execute("""
        SELECT security_answer_1, security_answer_2 
        FROM patients 
        WHERE email = 'test@example.com'
    """)
    result = cursor.fetchone()
    print(f"Updated answers: '{result[0]}' | '{result[1]}'")

except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()