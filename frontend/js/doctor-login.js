const API_URL = 'http://localhost:5000/api';

document.getElementById('doctorLoginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const loginData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };
    
    try {
        const response = await fetch(`${API_URL}/doctor/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(loginData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('doctorId', data.doctor_id);
            localStorage.setItem('doctorName', data.full_name);
            localStorage.setItem('doctorEmail', data.email);
            window.location.href = 'dashboard.html';
        } else {
            alert('✗ ' + data.message);
        }
    } catch (error) {
        alert('✗ Login failed. Please try again.');
        console.error('Error:', error);
    }
});
