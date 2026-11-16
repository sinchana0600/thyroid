let currentDoctorId = null;

// Step 1: Find account by email
document.getElementById('emailForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const messageDiv = document.getElementById('message');
    
    try {
        const response = await fetch('/api/doctor/forgot-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show security questions
            currentDoctorId = data.doctor_id;
            document.getElementById('securityQuestionLabel1').textContent = data.security_question_1;
            document.getElementById('securityQuestionLabel2').textContent = data.security_question_2;
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            messageDiv.innerHTML = '<div class="success">Account found! Please answer both security questions.</div>';
        } else {
            messageDiv.innerHTML = `<div class="error">${data.message}</div>`;
        }
    } catch (error) {
        messageDiv.innerHTML = '<div class="error">Network error. Please try again.</div>';
    }
});

// Step 2: Reset password with security answer
document.getElementById('securityForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const securityAnswer1 = document.getElementById('securityAnswer1').value;
    const securityAnswer2 = document.getElementById('securityAnswer2').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const messageDiv = document.getElementById('message');
    
    // Validate security answers
    if (!securityAnswer1.trim()) {
        messageDiv.innerHTML = '<div class="error">Please provide answer to first security question!</div>';
        return;
    }
    
    if (!securityAnswer2.trim()) {
        messageDiv.innerHTML = '<div class="error">Please provide answer to second security question!</div>';
        return;
    }
    
    // Validate passwords match
    if (newPassword !== confirmPassword) {
        messageDiv.innerHTML = '<div class="error">Passwords do not match!</div>';
        return;
    }
    
    if (newPassword.length < 6) {
        messageDiv.innerHTML = '<div class="error">Password must be at least 6 characters long!</div>';
        return;
    }
    
    try {
        const response = await fetch('/api/doctor/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                doctor_id: currentDoctorId,
                security_answer_1: securityAnswer1,
                security_answer_2: securityAnswer2,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.innerHTML = '<div class="success">Password reset successful! Redirecting to login...</div>';
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            messageDiv.innerHTML = `<div class="error">${data.message}</div>`;
        }
    } catch (error) {
        messageDiv.innerHTML = '<div class="error">Network error. Please try again.</div>';
    }
});