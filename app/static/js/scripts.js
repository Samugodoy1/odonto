// Global utility functions and event handlers

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle alerts auto-close
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000); // Auto-close after 5 seconds
    });
    
    // Handle form validations
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Add confirm dialog to critical actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = button.getAttribute('data-confirm');
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Enhance form inputs
    enhanceFormInputs();
});

// Function to format date inputs to the appropriate format
function formatDateInput(input) {
    input.addEventListener('blur', function() {
        if (!input.value) return;
        
        const parts = input.value.split('-');
        if (parts.length === 3) {
            // Already in ISO format
            return;
        }
        
        // Try to parse as DD/MM/YYYY
        const dateParts = input.value.split('/');
        if (dateParts.length === 3) {
            const day = dateParts[0].padStart(2, '0');
            const month = dateParts[1].padStart(2, '0');
            const year = dateParts[2].length === 2 ? '20' + dateParts[2] : dateParts[2];
            input.value = `${year}-${month}-${day}`;
        }
    });
}

// Function to format time inputs
function formatTimeInput(input) {
    input.addEventListener('blur', function() {
        if (!input.value) return;
        
        // Check if already in HH:MM format
        if (/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(input.value)) {
            // Ensure two digits for hour
            const parts = input.value.split(':');
            const hour = parts[0].padStart(2, '0');
            input.value = `${hour}:${parts[1]}`;
            return;
        }
        
        // Try to parse numeric input
        if (/^\d{1,4}$/.test(input.value)) {
            const val = input.value.padStart(4, '0');
            const hour = val.substring(0, 2);
            const minute = val.substring(2, 4);
            
            if (parseInt(hour) < 24 && parseInt(minute) < 60) {
                input.value = `${hour}:${minute}`;
            }
        }
    });
}

// Enhance various form inputs for better user experience
function enhanceFormInputs() {
    // Format date inputs
    document.querySelectorAll('input[type="date"]').forEach(formatDateInput);
    
    // Format time inputs
    document.querySelectorAll('input[name*="hora"]').forEach(formatTimeInput);
    
    // Auto-capitalize name inputs
    document.querySelectorAll('input[name*="nome"]').forEach(function(input) {
        input.addEventListener('blur', function() {
            if (!input.value) return;
            
            // Capitalize each word
            input.value = input.value.replace(/\b\w/g, c => c.toUpperCase());
        });
    });
}

// Function to copy text to clipboard
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    document.execCommand('copy');
    
    // Show success message
    const successElement = document.getElementById('copySuccess');
    if (successElement) {
        successElement.classList.remove('d-none');
        setTimeout(() => {
            successElement.classList.add('d-none');
        }, 3000);
    }
}
