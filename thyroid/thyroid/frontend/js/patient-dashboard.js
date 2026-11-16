const patientId = localStorage.getItem('patientId');
if (!patientId) {
    window.location.href = 'login.html';
}

const API_URL = 'http://localhost:5000/api';

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
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    
    if (page === 'book-appointment') loadDoctors();
    if (page === 'view-appointments') loadAppointments();
    if (page === 'reports') loadReports();
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
    if (confirm('Are you sure you want to logout?')) {
        const patientName = localStorage.getItem('patientName');
        localStorage.clear();
        
        // Redirect with success message
        window.location.href = 'login.html?logout=success';
    }
});

// Health Checkup - Progressive Analysis
function analyzeSleepWork() {
    const sleepHours = parseFloat(document.getElementById('sleepHours').value);
    const workingHours = parseFloat(document.getElementById('workingHours').value);
    
    // Validation for positive values and ranges
    if (!sleepHours || sleepHours <= 0 || sleepHours > 24) {
        showToast('⚠ Please enter valid sleep hours (0.1 - 24)', 'warning');
        return;
    }
    
    if (!workingHours || workingHours <= 0 || workingHours > 20) {
        showToast('⚠ Please enter valid working hours (0.1 - 20)', 'warning');
        return;
    }
    
    const tips = [];
    let healthScore = 0;
    
    // Sleep analysis
    if (sleepHours < 6) {
        tips.push('⚠️ You need more sleep! Aim for 7-9 hours per night to reduce stress and improve thyroid function.');
    } else if (sleepHours > 9) {
        tips.push('💤 Too much sleep can indicate thyroid issues. Consider getting checked if this persists.');
    } else {
        tips.push('✅ Great sleep habits! Keep maintaining 7-9 hours for optimal health.');
        healthScore++;
    }
    
    // Working hours analysis (mapped to stress levels for thyroid assessment)
    let stressEquivalent = Math.min(Math.ceil(workingHours / 2), 10); // Map working hours to stress scale 1-10
    
    if (workingHours > 12) {
        tips.push('⚠️ Long working hours can increase stress and affect thyroid function. Consider work-life balance.');
    } else if (workingHours > 8) {
        tips.push('⚖️ Moderate working hours. Ensure you take regular breaks and manage stress effectively.');
    } else {
        tips.push('✅ Good work-life balance! Reasonable working hours support overall health.');
        healthScore++;
    }
    
    const tipsDiv = document.getElementById('sleepStressTips');
    tipsDiv.innerHTML = '<h4>Sleep & Work Analysis</h4>';
    tips.forEach(tip => {
        tipsDiv.innerHTML += `<div class="tip-item">${tip}</div>`;
    });
    tipsDiv.style.display = 'block';
    
    return healthScore;
}

function analyzeBMI() {
    const height = parseFloat(document.getElementById('height').value);
    const weight = parseFloat(document.getElementById('weight').value);
    
    // Validation for positive values and realistic ranges
    if (!height || height <= 0 || height < 30 || height > 300) {
        showToast('⚠ Please enter valid height (30 - 300 cm)', 'warning');
        return;
    }
    
    if (!weight || weight <= 0 || weight > 500) {
        showToast('⚠ Please enter valid weight (1 - 500 kg)', 'warning');
        return;
    }
    
    const bmi = weight / ((height/100) ** 2);
    const tips = [];
    let healthScore = 0;
    
    if (bmi < 18.5) {
        tips.push(`⚖️ Your BMI is ${bmi.toFixed(1)} (Underweight). Ensure adequate nutrition as thyroid issues can affect weight.`);
    } else if (bmi > 25) {
        tips.push(`🏃 Your BMI is ${bmi.toFixed(1)} (Overweight). Consider regular exercise and balanced diet. Thyroid function affects metabolism.`);
    } else {
        tips.push(`✅ Your BMI is ${bmi.toFixed(1)} (Healthy range). Maintain with balanced diet and regular activity.`);
        healthScore++;
    }
    
    const tipsDiv = document.getElementById('bmiTips');
    tipsDiv.innerHTML = '<h4>BMI Analysis</h4>';
    tips.forEach(tip => {
        tipsDiv.innerHTML += `<div class="tip-item">${tip}</div>`;
    });
    tipsDiv.style.display = 'block';
    
    return healthScore;
}

function analyzeHydration() {
    const waterIntake = parseFloat(document.getElementById('waterIntake').value);
    const age = parseInt(document.getElementById('checkupAge').value);
    
    // Validation for positive values and realistic ranges
    if (!waterIntake || waterIntake <= 0 || waterIntake > 10) {
        showToast('⚠ Please enter valid water intake (0.1 - 10 liters)', 'warning');
        return;
    }
    
    if (!age || age <= 0 || age > 150) {
        showToast('⚠ Please enter valid age (1 - 150 years)', 'warning');
        return;
    }
    
    const recommendedWater = age < 30 ? 2.5 : age < 50 ? 2.0 : 1.8;
    const tips = [];
    let healthScore = 0;
    
    if (waterIntake < recommendedWater) {
        tips.push(`💧 Increase water intake to ${recommendedWater}L daily. Proper hydration supports thyroid function.`);
    } else {
        tips.push('✅ Excellent hydration! Water helps regulate metabolism and hormone balance.');
        healthScore++;
    }
    
    const tipsDiv = document.getElementById('hydrationTips');
    tipsDiv.innerHTML = '<h4>Hydration Analysis</h4>';
    tips.forEach(tip => {
        tipsDiv.innerHTML += `<div class="tip-item">${tip}</div>`;
    });
    tipsDiv.style.display = 'block';
    
    // Individual analysis complete - user can now perform comprehensive analysis
    
    return healthScore;
}

async function saveHealthCheckup(sleepHours, workingHours, height, weight, waterIntake, age) {
    try {
        const response = await fetch(`${API_URL}/health-checkup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_id: patientId,
                sleep_hours: sleepHours,
                working_hours: workingHours,
                height, weight, water_intake: waterIntake,
                health_tip: 'Complete health checkup performed'
            })
        });
        
        if (response.ok) {
            showToast('✓ Health checkup saved successfully!', 'success');
        }
    } catch (error) {
        console.error('Error saving checkup:', error);
    }
}

function generateHealthTips(sleep, stress, height, weight, water, age) {
    const tips = [];
    
    // Sleep & Stress tip
    if (sleep < 6) {
        tips.push('⚠️ You need more sleep! Aim for 7-9 hours per night to reduce stress and improve thyroid function.');
    } else if (sleep > 9) {
        tips.push('💤 Too much sleep can indicate thyroid issues. Consider getting checked if this persists.');
    } else {
        tips.push('✅ Great sleep habits! Keep maintaining 7-9 hours for optimal health.');
    }
    
    if (stress > 7) {
        tips.push('🧘 High stress affects thyroid hormones. Try meditation, yoga, or deep breathing exercises.');
    }
    
    // BMI tip
    const bmi = weight / ((height/100) ** 2);
    if (bmi < 18.5) {
        tips.push('⚖️ Your BMI is low. Ensure adequate nutrition as thyroid issues can affect weight.');
    } else if (bmi > 25) {
        tips.push('🏃 Consider regular exercise and balanced diet. Thyroid function affects metabolism.');
    } else {
        tips.push('✅ Healthy weight range! Maintain with balanced diet and regular activity.');
    }
    
    // Water & Age tip
    const recommendedWater = age < 30 ? 2.5 : age < 50 ? 2.0 : 1.8;
    if (water < recommendedWater) {
        tips.push(`💧 Increase water intake to ${recommendedWater}L daily. Proper hydration supports thyroid function.`);
    } else {
        tips.push('✅ Excellent hydration! Water helps regulate metabolism and hormone balance.');
    }
    
    return tips;
}

// Thyroid Check - Hybrid Approach with Auto-OCR
document.getElementById('reportImage').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    const ocrStatus = document.getElementById('ocrStatus');
    const imagePreview = document.getElementById('imagePreview');
    
    if (file) {
        // Show image preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Report Preview" style="max-width: 100%; border-radius: 8px; cursor: pointer;" onclick="document.getElementById('reportImage').click()">`;
        };
        reader.readAsDataURL(file);
        
        // Automatically process OCR
        ocrStatus.innerHTML = '<div class="ocr-processing"><span class="spinner"></span> Processing image with OCR...</div>';
        
        const formData = new FormData();
        formData.append('image', file);
        
        try {
            const response = await fetch(`${API_URL}/ocr-extract`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            console.log('OCR Response:', data); // Debug log
            
            if (data.tsh_value) {
                // Auto-fill TSH (required)
                document.getElementById('tshManual').value = data.tsh_value;
                console.log('TSH filled:', data.tsh_value);
                
                // Fill T3 if extracted (any positive value)
                if (data.t3_value && data.t3_value > 0) {
                    document.getElementById('t3Manual').value = data.t3_value;
                    console.log('T3 filled:', data.t3_value);
                } else {
                    console.log('T3 not found or zero:', data.t3_value);
                }
                
                // Fill T4 if extracted (any positive value)
                if (data.t4_value && data.t4_value > 0) {
                    document.getElementById('t4Manual').value = data.t4_value;
                    console.log('T4 filled:', data.t4_value);
                } else {
                    console.log('T4 not found or zero:', data.t4_value);
                }
                
                // Show detailed status with what was extracted
                let extractedValues = `TSH: ${data.tsh_value}`;
                let extractedCount = 1;
                
                if (data.t3_value && data.t3_value > 0) {
                    extractedValues += `, T3: ${data.t3_value}`;
                    extractedCount++;
                }
                if (data.t4_value && data.t4_value > 0) {
                    extractedValues += `, T4: ${data.t4_value}`;
                    extractedCount++;
                }
                
                let statusMessage = extractedCount === 3 
                    ? 'All values extracted successfully!' 
                    : 'TSH extracted. Fill missing values manually if needed.';
                
                ocrStatus.innerHTML = `
                    <div class="ocr-success">
                        <span class="success-icon">✓</span>
                        <div>
                            <strong>${statusMessage}</strong>
                            <p>Extracted: ${extractedValues}</p>
                            <p style="font-size: 0.85rem; margin-top: 5px; opacity: 0.8;">Please review and edit if needed.</p>
                        </div>
                    </div>
                `;
                showToast(`✓ OCR extracted ${extractedCount} value(s)`, 'success');
            } else {
                ocrStatus.innerHTML = `
                    <div class="ocr-warning">
                        <span class="warning-icon">⚠</span>
                        <div>
                            <strong>Could not extract values</strong>
                            <p>Please enter values manually in the right panel.</p>
                        </div>
                    </div>
                `;
                showToast('⚠ OCR failed. Please enter values manually', 'warning');
            }
        } catch (error) {
            ocrStatus.innerHTML = `
                <div class="ocr-error">
                    <span class="error-icon">✗</span>
                    <div>
                        <strong>OCR Processing Failed</strong>
                        <p>Please enter values manually in the right panel.</p>
                    </div>
                </div>
            `;
            showToast('✗ OCR error. Please enter values manually', 'error');
        }
    } else {
        imagePreview.innerHTML = `
            <div class="preview-placeholder" onclick="document.getElementById('reportImage').click()">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                </svg>
                <p>Click to upload image</p>
                <small>Supports: JPG, PNG, PDF</small>
            </div>`;
        ocrStatus.innerHTML = '';
    }
});

document.getElementById('thyroidCheckForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Validate symptoms selection
    const selectedSymptoms = document.querySelectorAll('.symptom-checkbox:checked');
    if (selectedSymptoms.length === 0) {
        showToast('⚠ Please select at least one symptom', 'warning');
        return;
    }
    
    // ALWAYS use manual field values (whether typed manually or auto-filled by OCR)
    const tsh = document.getElementById('tshManual').value;
    const t3 = document.getElementById('t3Manual').value;
    const t4 = document.getElementById('t4Manual').value;
    
    if (!tsh) {
        showToast('⚠ Please enter TSH value', 'warning');
        return;
    }
    
    // Collect symptoms
    const symptoms = Array.from(selectedSymptoms).map(cb => cb.value);
    
    // Prepare data - always send manual values
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('symptoms', symptoms.join(', '));
    formData.append('tsh_manual', tsh);
    formData.append('t3_manual', t3 || '0');
    formData.append('t4_manual', t4 || '0');
    
    // Optionally include image for record keeping
    const fileInput = document.getElementById('reportImage');
    if (fileInput.files[0]) {
        formData.append('image', fileInput.files[0]);
    }
    
    // Show immediate feedback
    showToast('🔍 Analyzing thyroid report...', 'info');
    
    try {
        const response = await fetch(`${API_URL}/thyroid-check`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        const resultDiv = document.getElementById('thyroidResult');
        if (data.error) {
            resultDiv.innerHTML = `
                <div class="thyroid-result-error">
                    <h3>⚠️ Analysis Error</h3>
                    <p>${data.message}</p>
                </div>
            `;
            showToast('⚠ ' + data.message, 'warning');
        } else {
            // Determine confidence color
            const confidence = data.confidence || 0;
            let confidenceColor = '#4caf50'; // green
            if (confidence < 70) confidenceColor = '#ff9800'; // orange
            if (confidence < 50) confidenceColor = '#f44336'; // red
            
            // Extract classification from result
            const resultText = data.result || '';
            let classification = 'Unknown';
            let classificationColor = '#666';
            
            if (resultText.includes('MALIGNANCY-SUSPECTED')) {
                classification = 'MALIGNANCY-SUSPECTED';
                classificationColor = '#d32f2f'; // Professional red
            } else if (resultText.includes('MALIGNANT RISK')) {
                classification = 'MALIGNANT RISK';
                classificationColor = '#d32f2f'; // Professional red
            } else if (resultText.includes('BENIGN (Monitor Required)')) {
                classification = 'BENIGN (Monitor Required)';
                classificationColor = '#f57c00'; // Professional orange for monitoring
            } else if (resultText.includes('BENIGN')) {
                classification = 'BENIGN';
                classificationColor = '#388e3c'; // Professional green
            }
            
            // Format the detailed result text for better display
            const formattedResult = resultText
                .replace(/🔬 THYROID ANALYSIS REPORT/g, '')
                .replace(/📊 CLASSIFICATION:/g, '<strong>📊 CLASSIFICATION:</strong>')
                .replace(/🏥 CONDITION:/g, '<strong>🏥 CONDITION:</strong>')
                .replace(/⚠️  RISK LEVEL:/g, '<strong>⚠️ RISK LEVEL:</strong>')
                .replace(/📈 CONFIDENCE:/g, '<strong>📈 CONFIDENCE:</strong>')
                .replace(/📋 DETAILED ANALYSIS:/g, '<strong>📋 DETAILED ANALYSIS:</strong>')
                .replace(/🩺 MEDICAL RECOMMENDATION:/g, '<strong>🩺 MEDICAL RECOMMENDATION:</strong>')
                .replace(/📌 INTERPRETATION:/g, '<strong>📌 INTERPRETATION:</strong>')
                .replace(/\n/g, '<br>')
                .trim();
            
            // Enhanced formatting with proper label/value structure and data attributes
            const cleanedResult = formattedResult
                .replace(/📊 CLASSIFICATION:.*?<br>/g, '') // Remove classification line
                .replace(/🔬 THYROID ANALYSIS REPORT<br>/g, '') // Remove header
                .replace(/📈 CONFIDENCE:.*?<br>/g, '') // Remove confidence line
                // Format each section with proper label-value structure and data attributes
                .replace(/🏥 CONDITION:\s*([^<]*?)(?=<br>|$)/g, '<div class="analysis-row" data-type="condition"><strong>🏥 CONDITION:</strong><span class="analysis-value">$1</span></div>')
                .replace(/⚠️\s*RISK LEVEL:\s*([^<]*?)(?=<br>|$)/g, '<div class="analysis-row" data-type="risk"><strong>⚠️ RISK LEVEL:</strong><span class="analysis-value">$1</span></div>')
                .replace(/🩺 MEDICAL RECOMMENDATION:\s*([^<]*?)(?=<br>|$)/g, '<div class="analysis-row" data-type="recommendation"><strong>🩺 MEDICAL RECOMMENDATION:</strong><span class="analysis-value">$1</span></div>')
                .replace(/📌 INTERPRETATION:\s*([^<]*?)(?=<br>|$)/g, '<div class="analysis-row" data-type="interpretation"><strong>📌 INTERPRETATION:</strong><span class="analysis-value">$1</span></div>')
                .replace(/📋 DETAILED ANALYSIS:\s*([^<]*?)(?=<br>|$)/g, '<div class="analysis-row" data-type="detailed"><strong>📋 DETAILED ANALYSIS:</strong><span class="analysis-value">$1</span></div>')
                // Clean up any remaining <br> tags and extra spaces
                .replace(/<br>/g, '')
                .replace(/\s+/g, ' ')
                .trim();

            resultDiv.innerHTML = `
                <div class="thyroid-analysis-result-single">
                    <!-- TOP: Classification and Confidence -->
                    <div class="result-header-row">
                        <div class="classification-main">
                            <div class="classification-badge-main" style="background-color: ${classificationColor};">
                                ${classification}
                            </div>
                        </div>
                        <div class="confidence-main">
                            <div class="confidence-label">Confidence</div>
                            <div class="confidence-value-main" style="color: ${confidenceColor};">${confidence.toFixed(1)}%</div>
                            <div class="confidence-bar-main">
                                <div class="confidence-fill-main" style="background: ${confidenceColor}; width: ${confidence}%;"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- SINGLE REPORT ANALYSIS SECTION -->
                    <div class="report-analysis-section">
                        <h3>📋 Report Analysis</h3>
                        
                        <!-- Test Values in single line format -->
                        <div class="test-values-inline">
                            <strong>Test Values:</strong> 
                            TSH: ${data.tsh_value || tsh} mIU/L${(data.t3_value || t3) > 0 ? `, T3: ${data.t3_value || t3} ng/dL` : ''}${(data.t4_value || t4) > 0 ? `, T4: ${data.t4_value || t4} µg/dL` : ''}
                        </div>
                        
                        <!-- Clean medical analysis -->
                        <div class="medical-analysis-content">
                            ${cleanedResult}
                        </div>
                    </div>
                </div>
            `;
            
            // Scroll to result smoothly
            setTimeout(() => {
                resultDiv.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start',
                    inline: 'nearest'
                });
            }, 300);
            
            showToast(`✓ Analysis complete with ${confidence.toFixed(1)}% confidence!`, 'success');
        }
    } catch (error) {
        document.getElementById('thyroidResult').innerHTML = `
            <div class="thyroid-result-error">
                <h3>⚠️ Connection Error</h3>
                <p>Failed to analyze report. Please check your connection and try again.</p>
            </div>
        `;
        showToast('✗ Failed to analyze report. Please try again.', 'error');
    }
});

// Load Doctors
async function loadDoctors() {
    try {
        const response = await fetch(`${API_URL}/doctors`);
        const doctors = await response.json();
        
        const select = document.getElementById('doctorSelect');
        select.innerHTML = '<option value="">Select a doctor</option>';
        
        doctors.forEach(doctor => {
            select.innerHTML += `
                <option value="${doctor.doctor_id}">
                    ${doctor.full_name} - ${doctor.specialization} (${doctor.available_days})
                </option>
            `;
        });
    } catch (error) {
        console.error('Error loading doctors:', error);
    }
}

// Book Appointment
document.getElementById('bookAppointmentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get time components
    const hour = document.getElementById('appointmentHour').value;
    const minute = document.getElementById('appointmentMinute').value;
    const ampm = document.querySelector('input[name="ampm"]:checked')?.value;
    
    // Validate time inputs
    if (!hour || !minute || !ampm) {
        showToast('⚠ Please select complete time (hour, minute, and AM/PM)', 'warning');
        return;
    }
    
    // Convert to 24-hour format for backend
    let hour24 = parseInt(hour);
    if (ampm === 'PM' && hour24 !== 12) {
        hour24 += 12;
    } else if (ampm === 'AM' && hour24 === 12) {
        hour24 = 0;
    }
    
    const appointmentTime = `${hour24.toString().padStart(2, '0')}:${minute}:00`;
    
    const appointmentData = {
        patient_id: patientId,
        doctor_id: document.getElementById('doctorSelect').value,
        appointment_date: document.getElementById('appointmentDate').value,
        appointment_time: appointmentTime,
        notes: document.getElementById('appointmentNotes').value
    };
    
    // Show immediate feedback
    showToast('📅 Checking availability...', 'info');
    
    try {
        const response = await fetch(`${API_URL}/appointments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(appointmentData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('✓ Appointment booked successfully!', 'success');
            document.getElementById('bookAppointmentForm').reset();
            // Reset radio buttons
            document.querySelectorAll('input[name="ampm"]').forEach(radio => radio.checked = false);
            setTimeout(() => navigateTo('view-appointments'), 1000);
        } else if (response.status === 409) {
            // Slot conflict - show popup with specific message
            showSlotConflictPopup(result.message);
        } else {
            showToast(`✗ ${result.message || 'Failed to book appointment. Please try again.'}`, 'error');
        }
    } catch (error) {
        showToast('✗ Connection error. Please check your internet.', 'error');
    }
});

// Show slot conflict popup
function showSlotConflictPopup(message = 'This slot is already booked. Please choose another slot. Thank you!') {
    const popup = document.createElement('div');
    popup.className = 'slot-conflict-popup';
    
    // Determine the appropriate title and icon based on the message
    let title = '⚠️ Booking Conflict';
    let icon = '⚠️';
    
    if (message.includes('You already have an appointment')) {
        title = '📅 Time Conflict';
        icon = '📅';
    } else if (message.includes('already booked with this doctor')) {
        title = '👨‍⚕️ Doctor Unavailable';
        icon = '👨‍⚕️';
    }
    
    popup.innerHTML = `
        <div class="slot-conflict-content">
            <h3>${icon} ${title}</h3>
            <p>${message}</p>
            <button onclick="closeSlotConflictPopup()">Choose Another Slot</button>
        </div>
    `;
    document.body.appendChild(popup);
}

// Close slot conflict popup
function closeSlotConflictPopup() {
    const popup = document.querySelector('.slot-conflict-popup');
    if (popup) {
        popup.remove();
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

// Load Appointments
async function loadAppointments() {
    try {
        const response = await fetch(`${API_URL}/appointments/${patientId}`);
        const appointments = await response.json();
        
        const listDiv = document.getElementById('appointmentsList');
        
        if (appointments.length === 0) {
            listDiv.innerHTML = '<p>No appointments found.</p>';
            return;
        }
        
        listDiv.innerHTML = '';
        appointments.forEach(apt => {
            listDiv.innerHTML += `
                <div class="appointment-card">
                    <h3>Appointment with ${apt.doctor_name}</h3>
                    <div class="appointment-info">
                        <strong>Specialization:</strong> ${apt.specialization}<br>
                        <strong>Date:</strong> ${apt.appointment_date}<br>
                        <strong>Time:</strong> ${formatTime12Hour(apt.appointment_time)}<br>
                        <strong>Status:</strong> <span class="status-${apt.status.toLowerCase()}">${apt.status}</span><br>
                        ${apt.notes ? `<strong>Notes:</strong> ${apt.notes}` : ''}
                    </div>
                    ${apt.status !== 'Cancelled' && apt.status !== 'Confirmed' && apt.status !== 'Completed' ? 
                        `<button class="btn-delete" onclick="deleteAppointment(${apt.appointment_id})">Cancel Appointment</button>` 
                        : apt.status === 'Confirmed' ? 
                        `<button class="btn-disabled" disabled>Cannot Cancel (Confirmed)</button>` :
                        apt.status === 'Completed' ?
                        `<button class="btn-disabled" disabled>Appointment Completed</button>` : ''}
                </div>
            `;
        });
    } catch (error) {
        document.getElementById('appointmentsList').innerHTML = '<p>Error loading appointments.</p>';
    }
}

// Delete Appointment
async function deleteAppointment(appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    
    try {
        const response = await fetch(`${API_URL}/appointments/${appointmentId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('✓ Appointment cancelled successfully', 'success');
            loadAppointments();
        } else {
            showToast('✗ Failed to cancel appointment', 'error');
        }
    } catch (error) {
        showToast('✗ Error cancelling appointment', 'error');
    }
}

// Load Reports
async function loadReports() {
    try {
        const response = await fetch(`${API_URL}/reports/${patientId}`);
        const reports = await response.json();
        
        const listDiv = document.getElementById('reportsList');
        
        if (reports.length === 0) {
            listDiv.innerHTML = '<p>No reports found.</p>';
            return;
        }
        
        listDiv.innerHTML = '';
        reports.forEach(report => {
            const reportDate = new Date(report.report_date).toLocaleDateString();
            
            // Extract BENIGN/MALIGNANT classification from test_result
            let classification = 'Unknown';
            let classificationColor = '#666';
            const testResult = report.test_result || '';
            
            if (testResult.includes('MALIGNANCY-SUSPECTED')) {
                classification = 'MALIGNANCY-SUSPECTED';
                classificationColor = '#d32f2f';
            } else if (testResult.includes('MALIGNANT RISK')) {
                classification = 'MALIGNANT RISK';
                classificationColor = '#d32f2f';
            } else if (testResult.includes('BENIGN (Monitor Required)')) {
                classification = 'BENIGN (Monitor Required)';
                classificationColor = '#f57c00';
            } else if (testResult.includes('BENIGN')) {
                classification = 'BENIGN';
                classificationColor = '#388e3c';
            }
            
            // Format the full analysis for compact detailed view
            const formattedAnalysis = testResult
                .replace(/🔬 THYROID ANALYSIS REPORT/g, '')
                .replace(/📊 CLASSIFICATION:.*?\n/g, '') // Remove classification line
                .replace(/📈 CONFIDENCE:.*?\n/g, '') // Remove confidence line
                .replace(/🏥 CONDITION:/g, '<strong>Condition:</strong>')
                .replace(/⚠️  RISK LEVEL:/g, '<br><strong>Risk Level:</strong>')
                .replace(/📋 DETAILED ANALYSIS:/g, '<br><strong>Analysis:</strong>')
                .replace(/🩺 MEDICAL RECOMMENDATION:/g, '<br><strong>Recommendation:</strong>')
                .replace(/📌 INTERPRETATION:/g, '<br><strong>Interpretation:</strong>')
                .replace(/\n\n/g, '<br>')
                .replace(/\n/g, ' ')
                .replace(/• /g, '<br>• ')
                .trim();
            
            listDiv.innerHTML += `
                <div class="report-card">
                    <div class="report-header">
                        <h3>Thyroid Test Report #${report.report_id}</h3>
                        <div class="report-classification" style="background-color: ${classificationColor};">
                            ${classification}
                        </div>
                    </div>
                    <div class="report-info">
                        <div class="report-date">
                            <strong>📅 Date:</strong> ${reportDate}
                        </div>
                        <div class="report-values">
                            <strong>📊 Test Values:</strong> 
                            TSH: ${report.tsh_value || 'N/A'} mIU/L${report.t3_value > 0 ? `, T3: ${report.t3_value} ng/dL` : ''}${report.t4_value > 0 ? `, T4: ${report.t4_value} µg/dL` : ''}
                        </div>
                    </div>
                    <div id="reportView_${report.report_id}" style="display: none;" class="full-report-view">
                        <div class="full-analysis-content">
                            ${formattedAnalysis}
                        </div>
                    </div>
                    <div class="report-actions">
                        <button class="btn-view-report" onclick="toggleReportView(${report.report_id})">
                            👁️ View Full Report
                        </button>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        document.getElementById('reportsList').innerHTML = '<p>Error loading reports.</p>';
    }
}

// Toggle Report View
function toggleReportView(reportId) {
    const viewDiv = document.getElementById(`reportView_${reportId}`);
    const button = event.target;
    
    if (viewDiv.style.display === 'none' || viewDiv.style.display === '') {
        viewDiv.style.display = 'block';
        button.textContent = '🔼 Hide Full Report';
    } else {
        viewDiv.style.display = 'none';
        button.textContent = '👁️ View Full Report';
    }
}



// Set minimum date for appointments
document.getElementById('appointmentDate').min = new Date().toISOString().split('T')[0];


// Toast Notification System
function showToast(message, type = 'success') {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Add icon based on type
    const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : type === 'warning' ? '⚠' : 'ℹ';
    toast.innerHTML = `<span style="font-size: 1.2rem;">${icon}</span><span>${message}</span>`;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Show welcome message on dashboard load
window.addEventListener('DOMContentLoaded', () => {
    const patientName = localStorage.getItem('patientName');
    if (patientName) {
        showToast(`Welcome back, ${patientName}!`, 'success');
    }
});

// Show perfect health popup
function showPerfectHealthPopup() {
    const popup = document.createElement('div');
    popup.className = 'perfect-health-popup';
    popup.innerHTML = `
        <div class="perfect-health-content">
            <div class="celebration-icon">🎉</div>
            <h3>🌟 Congratulations! 🌟</h3>
            <p>Your health parameters are perfect! You're maintaining excellent lifestyle habits that support optimal thyroid function and overall wellness.</p>
            <div class="health-badges">
                <span class="badge">✅ Optimal Sleep</span>
                <span class="badge">✅ Balanced Work</span>
                <span class="badge">✅ Healthy BMI</span>
                <span class="badge">✅ Good Hydration</span>
            </div>
            <p class="encouragement">Keep up the fantastic work! Your dedication to health is truly commendable.</p>
            <button onclick="closePerfectHealthPopup()">Thank You!</button>
        </div>
    `;
    document.body.appendChild(popup);
}

// Close perfect health popup
function closePerfectHealthPopup() {
    const popup = document.querySelector('.perfect-health-popup');
    if (popup) {
        popup.remove();
    }
}

// Comprehensive Thyroid Health Analysis
function performComprehensiveAnalysis() {
    const sleepHours = parseFloat(document.getElementById('sleepHours').value);
    const workingHours = parseFloat(document.getElementById('workingHours').value);
    const height = parseFloat(document.getElementById('height').value);
    const weight = parseFloat(document.getElementById('weight').value);
    const waterIntake = parseFloat(document.getElementById('waterIntake').value);
    const age = parseInt(document.getElementById('checkupAge').value);
    
    // Validate all fields are filled
    if (!sleepHours || !workingHours || !height || !weight || !waterIntake || !age) {
        showToast('⚠ Please complete all health assessment sections first', 'warning');
        return;
    }
    
    // Validate ranges
    if (sleepHours <= 0 || sleepHours > 24 || workingHours <= 0 || workingHours > 20 || 
        height <= 30 || height > 300 || weight <= 0 || weight > 500 || 
        waterIntake <= 0 || waterIntake > 10 || age <= 0 || age > 150) {
        showToast('⚠ Please ensure all values are within valid ranges', 'warning');
        return;
    }
    
    // Calculate BMI
    const bmi = weight / ((height/100) ** 2);
    
    // Map working hours to stress level (for thyroid assessment)
    const stressLevel = Math.min(Math.ceil(workingHours / 2), 10);
    
    // Thyroid Classification Logic
    const analysis = classifyThyroidHealth(sleepHours, stressLevel, bmi, waterIntake, age);
    
    // Display comprehensive results
    displayComprehensiveResults(analysis, sleepHours, workingHours, bmi, waterIntake, age);
    
    // Save the comprehensive checkup
    saveHealthCheckup(sleepHours, workingHours, height, weight, waterIntake, age);
}

// Classify thyroid health based on provided criteria
function classifyThyroidHealth(sleep, stress, bmi, hydration, age) {
    let normalIndicators = 0;
    let hypothyroidIndicators = 0;
    let hyperthyroidIndicators = 0;
    
    const indicators = {
        normal: [],
        hypothyroid: [],
        hyperthyroid: []
    };
    
    // Sleep Analysis
    if (sleep >= 7 && sleep <= 9) {
        normalIndicators++;
        indicators.normal.push('Optimal sleep duration (7-9 hours)');
    } else if (sleep > 9) {
        hypothyroidIndicators++;
        indicators.hypothyroid.push('Excessive sleep (>9 hours) - may indicate hypothyroidism');
    } else if (sleep < 6) {
        hyperthyroidIndicators++;
        indicators.hyperthyroid.push('Reduced sleep (<6 hours) - may indicate hyperthyroidism');
    }
    
    // Working Hours Analysis (mapped to stress levels for thyroid assessment)
    if (stress >= 3 && stress <= 6) {
        normalIndicators++;
        indicators.normal.push('Balanced work schedule (moderate hours)');
    } else if (stress >= 1 && stress <= 5) {
        hypothyroidIndicators++;
        indicators.hypothyroid.push('Light work schedule - may correlate with low energy patterns');
    } else if (stress >= 7 && stress <= 10) {
        hyperthyroidIndicators++;
        indicators.hyperthyroid.push('Heavy work schedule - may indicate high energy/stress patterns');
    }
    
    // BMI Analysis
    if (bmi >= 18.5 && bmi <= 24.9) {
        normalIndicators++;
        indicators.normal.push('Healthy BMI range (18.5-24.9)');
    } else if (bmi >= 25) {
        hypothyroidIndicators++;
        indicators.hypothyroid.push('Higher BMI (≥25) - weight gain may indicate hypothyroidism');
    } else if (bmi < 18.5) {
        hyperthyroidIndicators++;
        indicators.hyperthyroid.push('Low BMI (<18.5) - weight loss may indicate hyperthyroidism');
    }
    
    // Hydration Analysis
    if (hydration >= 2 && hydration <= 3) {
        normalIndicators++;
        indicators.normal.push('Optimal hydration (2-3 liters/day)');
    } else if (hydration < 2) {
        hypothyroidIndicators++;
        indicators.hypothyroid.push('Low hydration (<2L/day) - may indicate hypothyroidism');
    } else if (hydration > 3) {
        hyperthyroidIndicators++;
        indicators.hyperthyroid.push('High water intake (>3L/day) - may indicate hyperthyroidism');
    }
    
    // Determine classification
    let classification = 'Normal';
    let confidence = 'Low';
    let message = '';
    let recommendations = [];
    
    if (normalIndicators >= 3) {
        classification = 'Normal';
        confidence = 'High';
        message = 'Your health parameters indicate normal thyroid function! 🌟';
        recommendations = [
            'Continue maintaining your healthy lifestyle',
            'Regular exercise and balanced diet',
            'Annual thyroid screening as preventive care'
        ];
    } else if (hypothyroidIndicators >= 2) {
        classification = 'Possible Hypothyroidism';
        confidence = hypothyroidIndicators >= 3 ? 'High' : 'Moderate';
        message = 'Your symptoms may suggest hypothyroidism (underactive thyroid). ⚠️';
        recommendations = [
            'Consult an endocrinologist for proper evaluation',
            'Request TSH, T3, and T4 blood tests',
            'Monitor symptoms like fatigue, weight gain, cold sensitivity',
            'Consider iodine-rich foods in your diet'
        ];
    } else if (hyperthyroidIndicators >= 2) {
        classification = 'Possible Hyperthyroidism';
        confidence = hyperthyroidIndicators >= 3 ? 'High' : 'Moderate';
        message = 'Your symptoms may suggest hyperthyroidism (overactive thyroid). ⚠️';
        recommendations = [
            'Seek immediate medical consultation',
            'Request comprehensive thyroid function tests',
            'Monitor symptoms like rapid heartbeat, anxiety, weight loss',
            'Avoid excessive caffeine and stimulants'
        ];
    } else {
        classification = 'Mixed Indicators';
        confidence = 'Low';
        message = 'Your results show mixed indicators. Further evaluation recommended. 🤔';
        recommendations = [
            'Consult a healthcare provider for comprehensive assessment',
            'Consider thyroid function tests for clarity',
            'Monitor your symptoms over the next few weeks',
            'Maintain a health diary for patterns'
        ];
    }
    
    return {
        classification,
        confidence,
        message,
        indicators,
        recommendations,
        normalCount: normalIndicators,
        hypothyroidCount: hypothyroidIndicators,
        hyperthyroidCount: hyperthyroidIndicators
    };
}

// Display comprehensive analysis results
function displayComprehensiveResults(analysis, sleep, workingHours, bmi, hydration, age) {
    const resultsDiv = document.getElementById('comprehensiveResults');
    
    let confidenceColor = analysis.confidence === 'High' ? '#27ae60' : 
                         analysis.confidence === 'Moderate' ? '#f39c12' : '#e74c3c';
    
    let classificationColor = analysis.classification === 'Normal' ? '#27ae60' : '#e74c3c';
    
    resultsDiv.innerHTML = `
        <div class="comprehensive-analysis-card">
            <div class="analysis-header">
                <h3>🔬 Comprehensive Thyroid Health Assessment</h3>
                <div class="classification-badge" style="background: ${classificationColor}">
                    ${analysis.classification}
                </div>
            </div>
            
            <div class="analysis-summary">
                <p class="main-message">${analysis.message}</p>
                <div class="confidence-indicator">
                    <span>Confidence Level: </span>
                    <span style="color: ${confidenceColor}; font-weight: bold;">${analysis.confidence}</span>
                </div>
            </div>
            
            <div class="parameters-summary">
                <h4>📊 Your Health Parameters</h4>
                <div class="params-grid">
                    <div class="param-item">
                        <span class="param-label">Sleep:</span>
                        <span class="param-value">${sleep} hours</span>
                    </div>
                    <div class="param-item">
                        <span class="param-label">Working Hours:</span>
                        <span class="param-value">${workingHours} hours/day</span>
                    </div>
                    <div class="param-item">
                        <span class="param-label">BMI:</span>
                        <span class="param-value">${bmi.toFixed(1)}</span>
                    </div>
                    <div class="param-item">
                        <span class="param-label">Hydration:</span>
                        <span class="param-value">${hydration}L/day</span>
                    </div>
                </div>
            </div>
            
            <div class="indicators-section">
                <h4>🎯 Health Indicators Analysis</h4>
                ${analysis.indicators.normal.length > 0 ? `
                    <div class="indicator-group normal">
                        <h5>✅ Normal Indicators (${analysis.normalCount})</h5>
                        <ul>${analysis.indicators.normal.map(ind => `<li>${ind}</li>`).join('')}</ul>
                    </div>
                ` : ''}
                
                ${analysis.indicators.hypothyroid.length > 0 ? `
                    <div class="indicator-group hypothyroid">
                        <h5>⚠️ Hypothyroid Indicators (${analysis.hypothyroidCount})</h5>
                        <ul>${analysis.indicators.hypothyroid.map(ind => `<li>${ind}</li>`).join('')}</ul>
                    </div>
                ` : ''}
                
                ${analysis.indicators.hyperthyroid.length > 0 ? `
                    <div class="indicator-group hyperthyroid">
                        <h5>🔥 Hyperthyroid Indicators (${analysis.hyperthyroidCount})</h5>
                        <ul>${analysis.indicators.hyperthyroid.map(ind => `<li>${ind}</li>`).join('')}</ul>
                    </div>
                ` : ''}
            </div>
            
            <div class="recommendations-section">
                <h4>💡 Recommendations</h4>
                <ul class="recommendations-list">
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
            
            <div class="disclaimer">
                <p><strong>⚠️ Important Disclaimer:</strong> This assessment is lifestyle-based and NOT a medical diagnosis. 
                For accurate thyroid evaluation, please consult a healthcare provider and request laboratory thyroid tests 
                (TSH, T3, T4). Always seek professional medical advice for health concerns.</p>
            </div>
        </div>
    `;
    
    resultsDiv.style.display = 'block';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Show appropriate popup based on classification
    if (analysis.classification === 'Normal' && analysis.confidence === 'High') {
        setTimeout(() => showPerfectHealthPopup(), 1000);
    }
}