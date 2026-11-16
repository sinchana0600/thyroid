// Check for logout success message
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const messageDiv = document.getElementById('message');
    
    if (urlParams.get('logout') === 'success') {
        messageDiv.className = 'message success';
        messageDiv.textContent = '✓ Logged out successfully!';
        
        // Clear the URL parameter
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('message');
    
    // Show loading message
    messageDiv.className = 'message';
    messageDiv.style.display = 'block';
    messageDiv.style.background = '#e3f2fd';
    messageDiv.style.color = '#1976d2';
    messageDiv.textContent = 'Logging in...';
    
    try {
        const response = await fetch('http://localhost:5000/api/patient/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.className = 'message success';
            messageDiv.textContent = '✓ Login successful! Welcome back, ' + data.full_name + '!';
            localStorage.setItem('patientId', data.patient_id);
            localStorage.setItem('patientName', data.full_name);
            setTimeout(() => window.location.href = 'dashboard.html', 1500);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = '✗ ' + (data.message || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '✗ Connection error. Please make sure the server is running.';
    }
});
