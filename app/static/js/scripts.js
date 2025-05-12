// Main JavaScript file for Sistema Odontológico

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Auto-close alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add custom behavior for CPF and phone inputs
    setupInputMasks();
    
    // Current year for footer
    document.querySelectorAll('.current-year').forEach(function(el) {
        el.textContent = new Date().getFullYear();
    });
});

// Setup input masks for common fields
function setupInputMasks() {
    // CPF mask (000.000.000-00)
    const cpfInputs = document.querySelectorAll('input[id="cpf"]');
    cpfInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.substring(0, 11);
            
            if (value.length > 9) {
                value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})$/, "$1.$2.$3-$4");
            } else if (value.length > 6) {
                value = value.replace(/^(\d{3})(\d{3})(\d{1,3})$/, "$1.$2.$3");
            } else if (value.length > 3) {
                value = value.replace(/^(\d{3})(\d{1,3})$/, "$1.$2");
            }
            
            e.target.value = value;
        });
    });
    
    // Phone mask ((00) 00000-0000)
    const phoneInputs = document.querySelectorAll('input[id="telefone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.substring(0, 11);
            
            if (value.length > 10) {
                value = value.replace(/^(\d{2})(\d{5})(\d{4})$/, "($1) $2-$3");
            } else if (value.length > 6) {
                value = value.replace(/^(\d{2})(\d{4})(\d{1,4})$/, "($1) $2-$3");
            } else if (value.length > 2) {
                value = value.replace(/^(\d{2})(\d{1,5})$/, "($1) $2");
            }
            
            e.target.value = value;
        });
    });
    
    // Time mask (HH:MM)
    const timeInputs = document.querySelectorAll('input[id="hora_consulta"]');
    timeInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 4) value = value.slice(0, 4);
            
            if (value.length > 2) {
                // Make sure hour is valid (00-23)
                let hour = parseInt(value.substring(0, 2));
                if (hour > 23) hour = 23;
                
                // Make sure minute is valid (00-59)
                let minute = parseInt(value.substring(2));
                if (minute > 59) minute = 59;
                
                value = hour.toString().padStart(2, '0') + ':' + minute.toString().padStart(2, '0');
            } else if (value.length > 0) {
                value = value.padStart(2, '0') + ':';
            }
            
            e.target.value = value;
        });
    });
}

// Function to confirm actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format date for display (YYYY-MM-DD to DD/MM/YYYY)
function formatDate(dateString) {
    if (!dateString) return '';
    
    const parts = dateString.split('-');
    if (parts.length !== 3) return dateString;
    
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

// Parse date from display format (DD/MM/YYYY to YYYY-MM-DD)
function parseDate(dateString) {
    if (!dateString) return '';
    
    const parts = dateString.split('/');
    if (parts.length !== 3) return dateString;
    
    return `${parts[2]}-${parts[1]}-${parts[0]}`;
}
