const API_URL = 'http://localhost:5000/api';

document.getElementById('doctorRegisterForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }
    
    if (password.length < 6) {
        alert('Password must be at least 6 characters long!');
        return;
    }
    
    const doctorData = {
        full_name: document.getElementById('fullName').value,
        email: document.getElementById('email').value,
        password: password,
        phone: document.getElementById('phone').value,
        specialization: document.getElementById('specialization').value,
        available_days: document.getElementById('availableDays').value
    };
    
    try {
        const response = await fetch(`${API_URL}/doctor/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(doctorData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✓ Registration successful! Please login.');
            window.location.href = 'login.html';
        } else {
            alert('✗ ' + data.message);
        }
    } catch (error) {
        alert('✗ Registration failed. Please try again.');
        console.error('Error:', error);
    }
});
