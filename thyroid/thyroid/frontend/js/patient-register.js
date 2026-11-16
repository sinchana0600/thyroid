document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const messageDiv = document.getElementById('message');
    
    // Validate password match
    if (password !== confirmPassword) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Passwords do not match!';
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Password must be at least 6 characters long!';
        return;
    }
    
    // Validate security questions and answers
    const securityQuestion1 = document.getElementById('securityQuestion1').value;
    const securityAnswer1 = document.getElementById('securityAnswer1').value;
    const securityQuestion2 = document.getElementById('securityQuestion2').value;
    const securityAnswer2 = document.getElementById('securityAnswer2').value;
    
    if (!securityQuestion1) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Please select first security question!';
        return;
    }
    
    if (!securityAnswer1.trim()) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Please provide answer to first security question!';
        return;
    }
    
    if (securityAnswer1.trim().length < 2) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ First security answer must be at least 2 characters long!';
        return;
    }
    
    if (!securityQuestion2) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Please select second security question!';
        return;
    }
    
    if (!securityAnswer2.trim()) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Please provide answer to second security question!';
        return;
    }
    
    if (securityAnswer2.trim().length < 2) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Second security answer must be at least 2 characters long!';
        return;
    }
    
    if (securityQuestion1 === securityQuestion2) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Please choose different security questions!';
        return;
    }
    
    const formData = {
        full_name: document.getElementById('fullName').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        address: document.getElementById('address').value,
        password: password,
        security_question_1: document.getElementById('securityQuestion1').value,
        security_answer_1: document.getElementById('securityAnswer1').value,
        security_question_2: document.getElementById('securityQuestion2').value,
        security_answer_2: document.getElementById('securityAnswer2').value
    };
    
    // Show loading message
    messageDiv.className = 'message';
    messageDiv.style.display = 'block';
    messageDiv.style.background = '#e3f2fd';
    messageDiv.style.color = '#1976d2';
    messageDiv.textContent = 'Creating your account...';
    
    try {
        const response = await fetch('http://localhost:5000/api/patient/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.className = 'message success';
            messageDiv.textContent = '✓ Registration successful! Welcome, ' + formData.full_name + '! Redirecting to login...';
            
            // Disable form to prevent double submission
            document.getElementById('registerForm').querySelectorAll('input, select, button').forEach(el => el.disabled = true);
            
            setTimeout(() => window.location.href = 'login.html?registered=success', 2000);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = '✗ ' + (data.message || 'Registration failed. Please try again.');
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Connection error. Please make sure the server is running.';
    }
});
