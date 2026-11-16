const doctorId = localStorage.getItem('doctorId');
const doctorName = localStorage.getItem('doctorName');
const doctorEmail = localStorage.getItem('doctorEmail');

if (!doctorId) {
    window.location.href = 'login.html';
}

const API_URL = 'http://localhost:5000/api';

// Display doctor name
document.getElementById('doctorName').textContent = doctorName;

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        if (link.id === 'logoutBtn') return;
        e.preventDefault();
        const page = link.dataset.page;
        navigateTo(page);
    });
});

function navigateTo(page) {
    document.querySelectorAll('.page-content').forEach(p => p.style.display = 'none');
    document.getElementById(`${page}-page`).style.display = 'block';
    
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');
    
    if (page === 'appointments') loadAppointments();
    if (page === 'patient-reports') loadPatientReports();
    if (page === 'connect-doctors') loadDoctors();
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        window.location.href = 'login.html';
    }
});

// Load dashboard stats
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_URL}/doctor/appointments/${doctorId}`);
        const appointments = await response.json();
        
        const pendingCount = appointments.filter(a => a.status === 'Pending').length;
        document.getElementById('appointmentCount').textContent = 
            `${appointments.length} total (${pendingCount} pending)`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Convert 24-hour time to 12-hour format with AM/PM
function formatTime12Hour(time24) {
    if (!time24) return 'N/A';
    
    const [hours, minutes] = time24.split(':');
    let hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    
    if (hour === 0) {
        hour = 12;
    } else if (hour > 12) {
        hour = hour - 12;
    }
    
    return `${hour}:${minutes} ${ampm}`;
}

// Load appointments
let currentFilter = 'all';

async function loadAppointments(filter = 'all') {
    currentFilter = filter;
    try {
        const response = await fetch(`${API_URL}/doctor/appointments/${doctorId}`);
        const appointments = await response.json();
        
        const listDiv = document.getElementById('appointmentsList');
        
        if (appointments.length === 0) {
            listDiv.innerHTML = '<p>No appointments found.</p>';
            return;
        }
        
        // Filter appointments
        let filteredAppointments = appointments;
        if (filter !== 'all') {
            filteredAppointments = appointments.filter(a => a.status === filter);
        }
        
        if (filteredAppointments.length === 0) {
            listDiv.innerHTML = `<p>No ${filter} appointments found.</p>`;
            return;
        }
        
        listDiv.innerHTML = '';
        filteredAppointments.forEach(apt => {
            const statusClass = apt.status.toLowerCase();
            const canConfirm = apt.status === 'Pending';
            const canComplete = apt.status === 'Confirmed';
            
            listDiv.innerHTML += `
                <div class="appointment-card">
                    <h3>Appointment with ${apt.patient_name}</h3>
                    <div class="appointment-info">
                        <strong>Patient Email:</strong> ${apt.patient_email}<br>
                        <strong>Patient Phone:</strong> ${apt.patient_phone || 'N/A'}<br>
                        <strong>Date:</strong> ${apt.appointment_date}<br>
                        <strong>Time:</strong> ${formatTime12Hour(apt.appointment_time)}<br>
                        <strong>Status:</strong> <span class="status-${statusClass}">${apt.status}</span><br>
                        ${apt.notes ? `<strong>Notes:</strong> ${apt.notes}<br>` : ''}
                    </div>
                    <div style="margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
                        ${canConfirm ? `
                            <button class="btn-primary" onclick="updateAppointmentStatus(${apt.appointment_id}, 'Confirmed')">
                                ✓ Confirm Appointment
                            </button>
                        ` : ''}
                        ${canComplete ? `
                            <button class="btn-secondary" onclick="updateAppointmentStatus(${apt.appointment_id}, 'Completed')">
                                ✓ Mark as Completed
                            </button>
                        ` : ''}
                        <button class="btn-secondary" onclick="viewPatientReports(${apt.patient_id}, '${apt.patient_name}')">
                            📊 View Patient Reports
                        </button>
                        <button class="btn-secondary" onclick="contactPatient('${apt.patient_email}', '${apt.patient_name}')">
                            ✉️ Contact Patient
                        </button>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        document.getElementById('appointmentsList').innerHTML = '<p>Error loading appointments.</p>';
        console.error('Error:', error);
    }
}

function filterAppointments(status) {
    loadAppointments(status);
}

// Update appointment status
async function updateAppointmentStatus(appointmentId, newStatus) {
    if (!confirm(`Are you sure you want to change status to ${newStatus}?`)) return;
    
    try {
        const response = await fetch(`${API_URL}/doctor/appointments/${appointmentId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            showToast(`✓ Appointment ${newStatus.toLowerCase()} successfully!`, 'success');
            loadAppointments(currentFilter);
            loadDashboardStats();
        } else {
            showToast('✗ Failed to update appointment', 'error');
        }
    } catch (error) {
        showToast('✗ Error updating appointment', 'error');
        console.error('Error:', error);
    }
}

// Load patient reports
async function loadPatientReports() {
    try {
        const response = await fetch(`${API_URL}/doctor/patient-reports/${doctorId}`);
        const reports = await response.json();
        
        const listDiv = document.getElementById('patientReportsList');
        
        if (reports.length === 0) {
            listDiv.innerHTML = '<p>No patient reports found.</p>';
            return;
        }
        
        listDiv.innerHTML = '';
        reports.forEach(report => {
            const reportDate = new Date(report.report_date).toLocaleDateString();
            const tshStatus = report.tsh_value ? 
                (report.tsh_value < 0.4 ? '⚠️ Low' : report.tsh_value > 4.0 ? '⚠️ High' : '✓ Normal') : 
                'N/A';
            
            listDiv.innerHTML += `
                <div class="report-card">
                    <h3>Patient: ${report.patient_name}</h3>
                    <div class="report-info">
                        <strong>Report Date:</strong> ${reportDate}<br>
                        <strong>TSH:</strong> ${report.tsh_value || 'N/A'} mIU/L ${tshStatus}<br>
                        <strong>T3:</strong> ${report.t3_value || 0} ng/dL<br>
                        <strong>T4:</strong> ${report.t4_value || 0} µg/dL<br>
                        <strong>Symptoms:</strong> ${report.symptoms || 'None reported'}<br>
                        <strong>Diagnosis:</strong> ${report.test_result}
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="btn-secondary" onclick="contactPatient('${report.patient_email}', '${report.patient_name}')">
                            ✉️ Contact Patient
                        </button>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        document.getElementById('patientReportsList').innerHTML = '<p>Error loading reports.</p>';
        console.error('Error:', error);
    }
}

// View specific patient reports
function viewPatientReports(patientId, patientName) {
    navigateTo('patient-reports');
    // Filter to show only this patient's reports
    setTimeout(() => {
        const reportCards = document.querySelectorAll('.report-card');
        reportCards.forEach(card => {
            if (!card.textContent.includes(patientName)) {
                card.style.display = 'none';
            }
        });
    }, 500);
}

// Load other doctors
async function loadDoctors() {
    try {
        const response = await fetch(`${API_URL}/doctors`);
        const doctors = await response.json();
        
        const listDiv = document.getElementById('doctorsList');
        
        // Filter out current doctor
        const otherDoctors = doctors.filter(d => d.doctor_id != doctorId);
        
        if (otherDoctors.length === 0) {
            listDiv.innerHTML = '<p>No other doctors found.</p>';
            return;
        }
        
        listDiv.innerHTML = '';
        otherDoctors.forEach(doctor => {
            listDiv.innerHTML += `
                <div class="doctor-card" style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>${doctor.full_name}</h3>
                    <div style="margin: 10px 0;">
                        <strong>Specialization:</strong> ${doctor.specialization}<br>
                        <strong>Available:</strong> ${doctor.available_days}
                    </div>
                    <button class="btn-primary" onclick="contactDoctor('${doctor.email}', '${doctor.full_name}')">
                        ✉️ Contact Doctor
                    </button>
                </div>
            `;
        });
    } catch (error) {
        document.getElementById('doctorsList').innerHTML = '<p>Error loading doctors.</p>';
        console.error('Error:', error);
    }
}

// Contact doctor via Gmail
function contactDoctor(doctorEmailAddress, doctorNameToContact) {
    const subject = encodeURIComponent(`Consultation Request from Dr. ${doctorName}`);
    const body = encodeURIComponent(`Dear Dr. ${doctorNameToContact},\n\nI would like to discuss a case with you.\n\nBest regards,\nDr. ${doctorName}\n${doctorEmail}`);
    
    // Gmail compose URL format
    const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${doctorEmailAddress}&su=${subject}&body=${body}`;
    
    // Open in new tab
    window.open(gmailUrl, '_blank');
}

// Contact patient via Gmail
function contactPatient(patientEmail, patientName) {
    const subject = encodeURIComponent(`Follow-up from Dr. ${doctorName}`);
    const body = encodeURIComponent(`Dear ${patientName},\n\nI hope this message finds you well.\n\nBest regards,\nDr. ${doctorName}\n${doctorEmail}`);
    
    // Gmail compose URL format
    const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${patientEmail}&su=${subject}&body=${body}`;
    
    // Open in new tab
    window.open(gmailUrl, '_blank');
}

// Toast notification
function showToast(message, type = 'success') {
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';
    toast.innerHTML = `<span style="font-size: 1.2rem;">${icon}</span><span>${message}</span>`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Load initial data
loadDashboardStats();
