// ============================================
// MAIN JAVASCRIPT FOR CIRS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
    
    // Enable tooltips    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggers.forEach(function(element) {
        new bootstrap.Tooltip(element);
    });
});

// ============================================
// DATE FORMATTING FUNCTIONS
// ============================================

function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('sw-TZ', options);
}

function timeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const diff = Math.floor((now - past) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, seconds] of Object.entries(intervals)) {
        const count = Math.floor(diff / seconds);
        if (count > 0) {
            return `${count} ${unit}${count > 1 ? 's' : ''} iliyopita`;
        }
    }
    return 'Sasa hivi';
}

// ============================================
// CONFIRMATION FUNCTIONS
// ============================================

function confirmDelete(message = 'Je, una uhakika unataka kufuta?') {
    return confirm(message);
}

function confirmAction(message = 'Je, una uhakika unataka kuendelea?') {
    return confirm(message);
}

// ============================================
// AJAX FUNCTIONS
// ============================================

function ajaxRequest(url, method, data, successCallback, errorCallback) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
    };
    
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken.value;
    }
    
    const options = {
        method: method,
        headers: headers,
        credentials: 'same-origin'
    };
    
    if (data && method !== 'GET') {
        options.body = new URLSearchParams(data);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }
    
    fetch(url, options)
        .then(response => response.json())
        .then(data => {
            if (successCallback) successCallback(data);
        })
        .catch(error => {
            if (errorCallback) errorCallback(error);
        });
}

// ============================================
// FILE UPLOAD HELPER
// ============================================

function handleFileUpload(inputElement, previewElement) {
    const file = inputElement.files[0];
    if (!file) return;
    
    // Check file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
        alert('Faili ni kubwa sana! Inaruhusiwa hadi 50MB.');
        inputElement.value = '';
        return;
    }
    
    // Check file type
    const allowedTypes = ['.pdf', '.png', '.jpg', '.jpeg', '.txt', '.log', '.csv', '.xlsx', '.zip', '.rar'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(ext)) {
        alert('Aina ya faili hairuhusiwi! Ruhusiwa: ' + allowedTypes.join(', '));
        inputElement.value = '';
        return;
    }
    
    // Show file info
    if (previewElement) {
        const size = (file.size / 1024 / 1024).toFixed(2);
        previewElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center p-2 bg-light rounded">
                <div>
                    <i class="fas fa-file me-2"></i>
                    <strong>${file.name}</strong>
                    <small class="text-muted ms-2">(${size} MB)</small>
                </div>
                <button type="button" class="btn btn-sm btn-danger" onclick="removeFile(this)">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }
}

function removeFile(button) {
    const container = button.closest('.d-flex');
    if (container) {
        container.parentElement.innerHTML = '';
        const fileInput = container.parentElement.parentElement.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.value = '';
        }
    }
}