const API_URL = 'http://localhost:5000/api';

let currentEmail = '';

// Step 1: Request Reset Code
document.getElementById('forgotPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('resetEmail').value;
    const messageDiv = document.getElementById('emailMessage');
    
    if (!email) {
        showMessage(messageDiv, 'Please enter your email address', 'error');
        return;
    }
    
    currentEmail = email;
    
    try {
        showMessage(messageDiv, 'Sending reset code...', 'info');
        
        const response = await fetch(`${API_URL}/patient/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(messageDiv, result.message, 'success');
            setTimeout(() => {
                showStep('codeStep');
            }, 2000);
        } else {
            showMessage(messageDiv, result.message, 'error');
        }
    } catch (error) {
        showMessage(messageDiv, 'Network error. Please try again.', 'error');
    }
});

// Step 2: Verify Code
document.getElementById('verifyCodeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const code = document.getElementById('verificationCode').value;
    const messageDiv = document.getElementById('codeMessage');
    
    if (!code || code.length !== 6) {
        showMessage(messageDiv, 'Please enter a valid 6-digit code', 'error');
        return;
    }
    
    try {
        showMessage(messageDiv, 'Verifying code...', 'info');
        
        const response = await fetch(`${API_URL}/verify-reset-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: currentEmail, code })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(messageDiv, result.message, 'success');
            setTimeout(() => {
                showStep('passwordStep');
            }, 1500);
        } else {
            showMessage(messageDiv, result.message, 'error');
        }
    } catch (error) {
        showMessage(messageDiv, 'Network error. Please try again.', 'error');
    }
});

// Step 3: Set New Password
document.getElementById('newPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const password = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const messageDiv = document.getElementById('passwordMessage');
    
    if (!password || password.length < 6) {
        showMessage(messageDiv, 'Password must be at least 6 characters long', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showMessage(messageDiv, 'Passwords do not match', 'error');
        return;
    }
    
    try {
        showMessage(messageDiv, 'Resetting password...', 'info');
        
        const response = await fetch(`${API_URL}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: currentEmail, password })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(messageDiv, 'Password reset successfully! Redirecting to login...', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            showMessage(messageDiv, result.message, 'error');
        }
    } catch (error) {
        showMessage(messageDiv, 'Network error. Please try again.', 'error');
    }
});

// Resend Code Function
async function resendCode() {
    const messageDiv = document.getElementById('codeMessage');
    
    try {
        showMessage(messageDiv, 'Sending new code...', 'info');
        
        const response = await fetch(`${API_URL}/resend-reset-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: currentEmail })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(messageDiv, result.message, 'success');
            // Clear the code input
            document.getElementById('verificationCode').value = '';
        } else {
            showMessage(messageDiv, result.message, 'error');
        }
    } catch (error) {
        showMessage(messageDiv, 'Network error. Please try again.', 'error');
    }
}

// Utility Functions
function showStep(stepId) {
    // Hide all steps
    document.querySelectorAll('.reset-step').forEach(step => {
        step.style.display = 'none';
    });
    
    // Show target step
    document.getElementById(stepId).style.display = 'block';
}

function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    
    // Auto-hide success and info messages
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

// Auto-format verification code input
document.getElementById('verificationCode').addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, ''); // Remove non-digits
    if (value.length > 6) value = value.slice(0, 6); // Limit to 6 digits
    e.target.value = value;
});

// Password strength indicator
document.getElementById('newPassword').addEventListener('input', (e) => {
    const password = e.target.value;
    const messageDiv = document.getElementById('passwordMessage');
    
    if (password.length === 0) {
        messageDiv.style.display = 'none';
        return;
    }
    
    let strength = 'Weak';
    let color = '#e74c3c';
    
    if (password.length >= 8) {
        if (/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
            strength = 'Strong';
            color = '#27ae60';
        } else if (/(?=.*[a-z])(?=.*\d)/.test(password) || /(?=.*[A-Z])(?=.*\d)/.test(password)) {
            strength = 'Medium';
            color = '#f39c12';
        }
    } else if (password.length >= 6) {
        strength = 'Fair';
        color = '#f39c12';
    }
    
    showMessage(messageDiv, `Password strength: ${strength}`, 'info');
    messageDiv.style.color = color;
});