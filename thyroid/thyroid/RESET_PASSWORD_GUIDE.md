# Reset Password Functionality - Testing Guide

## Overview
The patient forgot password feature allows users to reset their password by answering two security questions that they set during registration.

## How It Works

### Step 1: Find Account
1. User enters their email address
2. System retrieves the security questions associated with that email
3. If email exists and has security questions, proceed to Step 2

### Step 2: Verify Security Answers & Reset Password
1. User sees their two security questions
2. User enters answers to both questions
3. User enters new password and confirms it
4. System validates:
   - Both security answers match (case-insensitive)
   - New password is at least 6 characters
   - Password and confirm password match
5. If valid, password is updated and user is redirected to login

## Testing the Reset Password Feature

### Test Account Credentials
A test patient account has been created with the following details:

**Login Credentials:**
- Email: `test@example.com`
- Password: `test123`

**Security Questions & Answers:**
- Question 1: "What is your favorite fruit?"
  - Answer: `apple`
- Question 2: "What school did you study in?"
  - Answer: `government school`

### Testing Steps

1. **Access the Forgot Password Page:**
   - Go to: http://localhost:5000/patient/login.html
   - Click on "Forgot Password?" link
   - OR directly visit: http://localhost:5000/patient/forgot-password.html

2. **Step 1 - Enter Email:**
   - Enter: `test@example.com`
   - Click "Find Account"
   - You should see the security questions appear

3. **Step 2 - Answer Security Questions:**
   - Security Answer 1: `apple`
   - Security Answer 2: `government school`
   - New Password: Enter any password (min 6 characters)
   - Confirm Password: Re-enter the same password
   - Click "Reset Password"

4. **Verify Success:**
   - You should see a success message
   - You will be redirected to the login page
   - Try logging in with the new password

## Database Schema

The patients table includes the following security-related columns:
```sql
security_question_1 VARCHAR(255)
security_answer_1 VARCHAR(255)
security_question_2 VARCHAR(255)
security_answer_2 VARCHAR(255)
```

## API Endpoints

### 1. Forgot Password - Step 1
**Endpoint:** `POST /api/patient/forgot-password`

**Request Body:**
```json
{
  "email": "test@example.com"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "patient_id": 1,
  "security_question_1": "What is your favorite fruit?",
  "security_question_2": "What school did you study in?",
  "message": "Please answer both security questions"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Email not found"
}
```

### 2. Reset Password - Step 2
**Endpoint:** `POST /api/patient/reset-password`

**Request Body:**
```json
{
  "patient_id": 1,
  "security_answer_1": "apple",
  "security_answer_2": "government school",
  "new_password": "newpassword123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password reset successful! You can now login with your new password."
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Incorrect security answers. Both answers must be correct."
}
```

## Common Issues & Solutions

### Issue 1: "Email not found"
**Cause:** The email doesn't exist in the database or patient hasn't registered yet.
**Solution:** Register a new account first or use the test account: test@example.com

### Issue 2: "Security questions not set"
**Cause:** Patient registered before security questions were added to the database.
**Solution:** 
- Run `python setup_database.py` to add security question columns
- Register a new account (security questions are now required)

### Issue 3: "Incorrect security answers"
**Cause:** The answers don't match what was stored during registration.
**Solution:** 
- Answers are case-insensitive, so "Apple" = "apple"
- Make sure there are no extra spaces
- For test account, use: "apple" and "government school"

### Issue 4: Reset button not working
**Cause:** Could be a frontend JavaScript error or backend validation issue.
**Solution:**
- Check browser console for JavaScript errors (F12)
- Check backend logs for error messages
- Ensure all form fields are filled correctly

## Security Features

1. **Password Hashing:** All passwords are hashed using Werkzeug's `generate_password_hash`
2. **Case-Insensitive Comparison:** Security answers are compared in lowercase
3. **Two-Factor Verification:** Requires both security questions to be answered correctly
4. **Minimum Password Length:** New password must be at least 6 characters

## Files Involved

### Frontend:
- `frontend/patient/forgot-password.html` - UI for password reset
- `frontend/js/forgot-password.js` - JavaScript logic for form handling
- `frontend/css/auth.css` - Styling for the forgot password page

### Backend:
- `backend/app.py` - API endpoints for forgot password and reset password
  - Line 168: `/api/patient/forgot-password` endpoint
  - Line 204: `/api/patient/reset-password` endpoint

### Database:
- `setup_database.py` - Creates patients table with security question columns
- `database/schema.sql` - Database schema definition

## Creating Additional Test Accounts

To create more test accounts with security questions, you can:

1. **Register through the UI:**
   - Go to http://localhost:5000/patient/register.html
   - Fill in all fields including security questions
   - Submit the form

2. **Use the test script:**
   - Run: `python create_test_patient.py`
   - This creates a test account with predefined security questions

## Debugging

If you need to debug the reset password functionality:

1. **Check Backend Logs:**
   - The backend now includes debug print statements
   - Look for lines starting with "Debug -"
   - These show the comparison between stored and provided answers

2. **Check Database:**
   ```sql
   USE thyroid_detection;
   SELECT patient_id, email, security_question_1, security_answer_1, 
          security_question_2, security_answer_2 
   FROM patients 
   WHERE email = 'test@example.com';
   ```

3. **Browser Console:**
   - Open Developer Tools (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab to see API request/response

## Summary

The reset password functionality is fully implemented and working. The key points are:

✅ Security questions are set during registration
✅ Two-step verification process (email → security questions)
✅ Case-insensitive answer comparison
✅ Password hashing for security
✅ User-friendly error messages
✅ Automatic redirect to login after successful reset

Test it using the provided test account or create your own account through the registration page!
