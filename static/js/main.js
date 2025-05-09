// Main JavaScript file for the Patient Management System

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Enable Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert.alert-dismissible');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Enable datepicker for date inputs if the browser doesn't support it natively
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs.length > 0) {
        dateInputs.forEach(input => {
            if (input.type !== 'date') {
                // Fallback for browsers that don't support date input
                input.setAttribute('placeholder', 'YYYY-MM-DD');
            }
        });
    }
    
    // Handle image preview for radiographs
    const radiographThumbnails = document.querySelectorAll('.radiograph-thumbnail');
    if (radiographThumbnails.length > 0) {
        radiographThumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                const imageUrl = this.src;
                const description = this.getAttribute('data-description') || '';
                const modalImage = document.getElementById('radiographModalImage');
                const modalDescription = document.getElementById('radiographModalDescription');
                
                if (modalImage && modalDescription) {
                    modalImage.src = imageUrl;
                    modalDescription.textContent = description;
                    const radiographModal = new bootstrap.Modal(document.getElementById('radiographModal'));
                    radiographModal.show();
                }
            });
        });
    }
    
    // Confirm deletion prompts
    const deleteButtons = document.querySelectorAll('.btn-delete');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Esta operação não pode ser desfeita. Deseja continuar?')) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.getElementById('searchForm').submit();
            }
        });
    }
    
    // CPF validation and formatting
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('blur', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length === 11) {
                value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
                this.value = value;
            }
        });
    }
    
    // Phone number formatting
    const phoneInput = document.getElementById('telefone');
    if (phoneInput) {
        phoneInput.addEventListener('blur', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length === 11) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
                this.value = value;
            }
        });
    }
    
    // Print patient record function
    const printButton = document.getElementById('printRecord');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
});

// Function to validate patient form
function validatePatientForm() {
    const nome = document.getElementById('nome').value.trim();
    const cpf = document.getElementById('cpf').value.trim();
    
    if (nome === '') {
        alert('O nome do paciente é obrigatório.');
        return false;
    }
    
    if (cpf === '') {
        alert('O CPF do paciente é obrigatório.');
        return false;
    }
    
    return true;
}

// Function to validate evolution form
function validateEvolutionForm() {
    const data = document.getElementById('data').value.trim();
    const procedimento = document.getElementById('procedimento').value.trim();
    
    if (data === '') {
        alert('A data do atendimento é obrigatória.');
        return false;
    }
    
    if (procedimento === '') {
        alert('O procedimento é obrigatório.');
        return false;
    }
    
    return true;
}

// Function to validate radiograph upload
function validateRadiographForm() {
    const radiografia = document.getElementById('radiografia');
    
    if (!radiografia.files || radiografia.files.length === 0) {
        alert('Selecione um arquivo para upload.');
        return false;
    }
    
    // Check file extension
    const fileName = radiografia.files[0].name;
    const fileExt = fileName.split('.').pop().toLowerCase();
    const allowedExts = ['jpg', 'jpeg', 'png', 'gif'];
    
    if (!allowedExts.includes(fileExt)) {
        alert('Formatos de arquivo permitidos: ' + allowedExts.join(', '));
        return false;
    }
    
    return true;
}
