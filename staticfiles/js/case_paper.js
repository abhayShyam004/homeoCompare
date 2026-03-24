/* Case Paper JavaScript - Fixed Version */

const AUTOSAVE_INTERVAL = 2 * 60 * 1000; // 2 minutes
let autoSaveTimer = null;
let formData = {};
let isDirty = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    setupEventListeners();
    loadCaseData();
    startAutoSave();
    updateProgressBar();
});

// Initialize Form
function initializeForm() {
    const form = document.getElementById('caseForm');
    if (!form) return;

    // Mark form as modified when any input changes
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            isDirty = true;
            updateProgressBar();
        });
        input.addEventListener('input', () => {
            updateProgressBar();
        });
    });
}

// Setup Event Listeners for Collapsible Sections
function setupEventListeners() {
    const headers = document.querySelectorAll('.cp-section-header');
    headers.forEach(header => {
        header.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.closest('.cp-form-section');
            if (section) {
                section.classList.toggle('cp-section-open');
            }
        });
    });

    // Open first section by default
    const firstSection = document.querySelector('.cp-form-section');
    if (firstSection) {
        firstSection.classList.add('cp-section-open');
    }
}

// Load Case Data
async function loadCaseData() {
    const form = document.getElementById('caseForm');
    if (!form) return;

    const caseId = form.dataset.caseId;
    if (!caseId) return;

    try {
        const response = await fetch(`/api/case_paper/get/${caseId}/`);
        if (!response.ok) return;

        const data = await response.json();
        populateForm(data);
    } catch (error) {
        console.error('Error loading case data:', error);
    }
}

// Populate Form
function populateForm(data) {
    Object.keys(data).forEach(key => {
        const value = data[key];
        
        if (key === 'chief_complaints' && Array.isArray(value)) {
            populateComplaints(value);
        } else if (key === 'followup' && Array.isArray(value)) {
            populateFollowups(value);
        } else if (typeof value === 'object' && value !== null && key !== 'case_id') {
            populateNestedFields(key, value);
        } else if (typeof value === 'string') {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) input.value = value;
        }
    });

    isDirty = false;
    updateProgressBar();
}

// Populate Nested Fields
function populateNestedFields(parentKey, obj) {
    Object.keys(obj).forEach(key => {
        const value = obj[key];
        if (typeof value === 'object' && value !== null) {
            populateNestedFields(`${parentKey}[${key}]`, value);
        } else {
            const fieldName = `${parentKey}[${key}]`;
            const input = document.querySelector(`[name="${fieldName}"]`);
            if (input) input.value = value || '';
        }
    });
}

// Populate Complaints
function populateComplaints(complaints) {
    const list = document.getElementById('complaintsList');
    if (!list) return;

    list.innerHTML = '';
    complaints.forEach((complaint) => {
        addComplaint(complaint, false);
    });
}

// Populate Followups
function populateFollowups(followups) {
    const list = document.getElementById('followupList');
    if (!list) return;

    list.innerHTML = '';
    followups.forEach((followup) => {
        addFollowup(followup, false);
    });
}

// Add Complaint
function addComplaint(data = null, showToast = true) {
    const list = document.getElementById('complaintsList');
    if (!list) return;

    const id = Date.now();
    const html = `
        <div class="cp-dynamic-item" data-complaint-id="${id}">
            <button type="button" class="cp-remove-item" onclick="removeComplaint(this)">
                <i class="fas fa-times"></i>
            </button>
            <div class="cp-form-row">
                <div class="cp-form-group">
                    <label>Complaint Name</label>
                    <input type="text" class="cp-input complaint-name" placeholder="e.g., Fever, Cough" value="${data?.name || ''}">
                </div>
                <div class="cp-form-group">
                    <label>Duration</label>
                    <input type="text" class="cp-input" placeholder="e.g., 3 days" value="${data?.duration || ''}">
                </div>
                <div class="cp-form-group">
                    <label>Location</label>
                    <input type="text" class="cp-input" placeholder="e.g., Head, Throat" value="${data?.location || ''}">
                </div>
            </div>
            <div class="cp-form-row">
                <div class="cp-form-group">
                    <label>Sensation</label>
                    <input type="text" class="cp-input" placeholder="e.g., Burning, Throbbing" value="${data?.sensation || ''}">
                </div>
                <div class="cp-form-group">
                    <label>Intensity (1-10)</label>
                    <input type="number" class="cp-input" min="1" max="10" placeholder="7" value="${data?.intensity || ''}">
                </div>
            </div>
            <div class="cp-form-row">
                <div class="cp-form-group">
                    <label>Aggravation (Worse)</label>
                    <textarea class="cp-textarea" rows="2" placeholder="e.g., worse at night, with heat">${data?.aggravation || ''}</textarea>
                </div>
                <div class="cp-form-group">
                    <label>Amelioration (Better)</label>
                    <textarea class="cp-textarea" rows="2" placeholder="e.g., better with rest, cold drinks">${data?.amelioration || ''}</textarea>
                </div>
            </div>
            <div class="cp-form-group">
                <label>Concomitants</label>
                <textarea class="cp-textarea" rows="2" placeholder="Other symptoms present">${data?.concomitants || ''}</textarea>
            </div>
        </div>
    `;

    const div = document.createElement('div');
    div.innerHTML = html;
    list.appendChild(div.firstElementChild);

    if (showToast) showToast_('Complaint added');
    isDirty = true;
    updateProgressBar();
}

// Remove Complaint
function removeComplaint(btn) {
    btn.closest('.cp-dynamic-item').remove();
    isDirty = true;
    showToast_('Complaint removed');
    updateProgressBar();
}

// Add Followup
function addFollowup(data = null, showToast = true) {
    const list = document.getElementById('followupList');
    if (!list) return;

    const id = Date.now();
    const html = `
        <div class="cp-dynamic-item" data-followup-id="${id}">
            <button type="button" class="cp-remove-item" onclick="removeFollowup(this)">
                <i class="fas fa-times"></i>
            </button>
            <div class="cp-form-row">
                <div class="cp-form-group">
                    <label>Follow-up Date</label>
                    <input type="date" class="cp-input" value="${data?.date || ''}">
                </div>
                <div class="cp-form-group">
                    <label>Overall Feeling</label>
                    <select class="cp-input">
                        <option value="">Select</option>
                        <option value="Much Better" ${data?.overall_feeling === 'Much Better' ? 'selected' : ''}>Much Better</option>
                        <option value="Better" ${data?.overall_feeling === 'Better' ? 'selected' : ''}>Better</option>
                        <option value="No Change" ${data?.overall_feeling === 'No Change' ? 'selected' : ''}>No Change</option>
                        <option value="Worse" ${data?.overall_feeling === 'Worse' ? 'selected' : ''}>Worse</option>
                    </select>
                </div>
            </div>
            <div class="cp-form-group">
                <label>Changes Observed</label>
                <textarea class="cp-textarea" rows="2" placeholder="What changes have occurred?">${data?.changes || ''}</textarea>
            </div>
            <div class="cp-form-group">
                <label>Assessment</label>
                <textarea class="cp-textarea" rows="2" placeholder="Your assessment...">${data?.assessment || ''}</textarea>
            </div>
            <div class="cp-form-group">
                <label>New Symptoms</label>
                <textarea class="cp-textarea" rows="2" placeholder="Any new symptoms?">${data?.new_symptoms || ''}</textarea>
            </div>
            <div class="cp-form-group">
                <label>Next Follow-up</label>
                <input type="text" class="cp-input" placeholder="e.g., After 1 week" value="${data?.next_followup || ''}">
            </div>
        </div>
    `;

    const div = document.createElement('div');
    div.innerHTML = html;
    list.appendChild(div.firstElementChild);

    if (showToast) showToast_('Follow-up entry added');
    isDirty = true;
    updateProgressBar();
}

// Remove Followup
function removeFollowup(btn) {
    btn.closest('.cp-dynamic-item').remove();
    isDirty = true;
    showToast_('Follow-up entry removed');
    updateProgressBar();
}

// Collect Form Data
function collectFormData() {
    const form = document.getElementById('caseForm');
    if (!form) return null;

    const formDataObj = {
        case_id: form.dataset.caseId || '',
        status: 'draft',
        preliminary: {},
        chief_complaints: [],
        associated_complaints: '',
        history: {},
        generals: {},
        clinical: {},
        analysis: {},
        prescription: {},
        followup: [],
        notes: ''
    };

    // Collect text inputs
    form.querySelectorAll('input, textarea, select').forEach(input => {
        const name = input.name;
        if (!name) return;

        const value = input.value.trim();

        if (name.startsWith('preliminary[')) {
            const key = name.match(/\[(.*?)\]/)[1];
            formDataObj.preliminary[key] = value;
        } else if (name.startsWith('history[')) {
            const matches = name.match(/\[(.*?)\]/g);
            if (matches.length === 1) {
                const key = matches[0].slice(1, -1);
                formDataObj.history[key] = value;
            } else if (matches.length === 2) {
                const key1 = matches[0].slice(1, -1);
                const key2 = matches[1].slice(1, -1);
                if (!formDataObj.history[key1]) formDataObj.history[key1] = {};
                formDataObj.history[key1][key2] = value;
            }
        } else if (name.startsWith('generals[')) {
            const key = name.match(/\[(.*?)\]/)[1];
            formDataObj.generals[key] = value;
        } else if (name.startsWith('clinical[')) {
            const key = name.match(/\[(.*?)\]/)[1];
            formDataObj.clinical[key] = value;
        } else if (name.startsWith('analysis[')) {
            const key = name.match(/\[(.*?)\]/)[1];
            formDataObj.analysis[key] = value;
        } else if (name.startsWith('prescription[')) {
            const key = name.match(/\[(.*?)\]/)[1];
            formDataObj.prescription[key] = value;
        } else if (name === 'associated_complaints') {
            formDataObj.associated_complaints = value;
        } else if (name === 'notes') {
            formDataObj.notes = value;
        }
    });

    // Collect complaints
    document.querySelectorAll('#complaintsList .cp-dynamic-item').forEach(item => {
        const complaint = {};
        item.querySelectorAll('input, textarea').forEach(input => {
            const placeholder = input.placeholder;
            if (placeholder.includes('Complaint Name')) complaint.name = input.value.trim();
            if (placeholder.includes('Duration')) complaint.duration = input.value.trim();
            if (placeholder.includes('Location')) complaint.location = input.value.trim();
            if (placeholder.includes('Sensation')) complaint.sensation = input.value.trim();
            if (placeholder.includes('Intensity')) complaint.intensity = input.value.trim();
            if (placeholder.includes('Worse')) complaint.aggravation = input.value.trim();
            if (placeholder.includes('Better')) complaint.amelioration = input.value.trim();
            if (placeholder.includes('Other symptoms')) complaint.concomitants = input.value.trim();
        });
        if (complaint.name) formDataObj.chief_complaints.push(complaint);
    });

    // Collect followups
    document.querySelectorAll('#followupList .cp-dynamic-item').forEach(item => {
        const followup = {};
        item.querySelectorAll('input, textarea, select').forEach(input => {
            if (input.type === 'date') followup.date = input.value;
            if (input.tagName === 'SELECT') followup.overall_feeling = input.value;
            
            const placeholder = input.placeholder;
            if (placeholder.includes('changes')) followup.changes = input.value.trim();
            if (placeholder.includes('assessment')) followup.assessment = input.value.trim();
            if (placeholder.includes('new symptoms')) followup.new_symptoms = input.value.trim();
            if (placeholder.includes('follow-up')) followup.next_followup = input.value.trim();
        });
        if (followup.date) formDataObj.followup.push(followup);
    });

    return formDataObj;
}

// Save Draft
async function saveDraft() {
    const data = collectFormData();
    if (!data) {
        showToast_('Error collecting form data', 'error');
        return;
    }

    // Check minimum required fields
    const patientName = data.preliminary.patient_name;
    if (!patientName || !patientName.trim()) {
        showToast_('Please enter patient name', 'error');
        return;
    }

    data.status = 'draft';

    try {
        const response = await fetch('/api/case_paper/full_save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            showToast_('Error saving case', 'error');
            return;
        }

        const result = await response.json();
        if (result.status === 'ok') {
            document.getElementById('caseForm').dataset.caseId = result.case_id;
            showToast_('Draft saved');
            isDirty = false;
        }
    } catch (error) {
        showToast_('Error: ' + error.message, 'error');
    }
}

// Mark Complete
async function markComplete() {
    const data = collectFormData();
    if (!data) {
        showToast_('Error collecting form data', 'error');
        return;
    }

    const patientName = data.preliminary.patient_name;
    const remedy = data.prescription.final_remedy;
    
    if (!patientName || !patientName.trim()) {
        showToast_('Please enter patient name', 'error');
        return;
    }

    if (!remedy || !remedy.trim()) {
        showToast_('Please select a remedy', 'error');
        return;
    }

    data.status = 'complete';

    try {
        const response = await fetch('/api/case_paper/full_save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            showToast_('Error saving case', 'error');
            return;
        }

        const result = await response.json();
        if (result.status === 'ok') {
            showToast_('Case completed!');
            setTimeout(() => {
                window.location.href = `/case_paper/${result.case_id}/`;
            }, 1500);
        }
    } catch (error) {
        showToast_('Error: ' + error.message, 'error');
    }
}

// Auto-save
function startAutoSave() {
    autoSaveTimer = setInterval(() => {
        if (isDirty) {
            saveDraft();
        }
    }, AUTOSAVE_INTERVAL);
}

// Stop Auto-save
function stopAutoSave() {
    if (autoSaveTimer) {
        clearInterval(autoSaveTimer);
        autoSaveTimer = null;
    }
}

// Update Progress Bar
function updateProgressBar() {
    const form = document.getElementById('caseForm');
    if (!form) return;

    // Count all inputs to show overall completion
    const allInputs = form.querySelectorAll('input[type="text"], input[type="date"], input[type="time"], input[type="number"], textarea, select');
    let totalInputs = allInputs.length;
    let filledInputs = 0;

    allInputs.forEach(input => {
        const val = input.value.trim();
        if (val && val.length > 0) {
            filledInputs++;
        }
    });

    const percentage = totalInputs > 0 ? Math.round((filledInputs / totalInputs) * 100) : 0;
    const progressFill = document.querySelector('.cp-progress-fill');
    const progressPercent = document.querySelector('.cp-progress-percent');

    if (progressFill) progressFill.style.width = percentage + '%';
    if (progressPercent) progressPercent.textContent = percentage;
}

// Show Toast
function showToast_(message, type = 'success') {
    const toast = document.getElementById('toastNotification');
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add('show');
    toast.classList.toggle('error', type === 'error');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Before unload warning
window.addEventListener('beforeunload', function(e) {
    if (isDirty) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes.';
    }
});

// Cleanup
window.addEventListener('unload', function() {
    stopAutoSave();
});
