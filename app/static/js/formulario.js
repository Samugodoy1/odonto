// Função para copiar o link para a área de transferência
function copyFormularioLink(linkId) {
    const linkElement = document.getElementById(linkId);
    const linkUrl = linkElement.textContent || linkElement.innerText;
    
    navigator.clipboard.writeText(linkUrl).then(function() {
        // Cria uma mensagem de sucesso
        const alertElement = document.createElement('div');
        alertElement.className = 'alert alert-success alert-dismissible fade show mt-2';
        alertElement.role = 'alert';
        alertElement.innerHTML = `
            <i class="bi bi-check-circle-fill me-2"></i>
            Link copiado para a área de transferência!
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        
        // Adiciona a mensagem após o elemento do link
        linkElement.parentNode.insertBefore(alertElement, linkElement.nextSibling);
        
        // Remove a mensagem após 3 segundos
        setTimeout(function() {
            alertElement.classList.remove('show');
            setTimeout(function() {
                alertElement.remove();
            }, 150);
        }, 3000);
    }).catch(function(err) {
        console.error('Erro ao copiar o link: ', err);
    });
}

// Função para compartilhar o link via WhatsApp
function shareViaWhatsApp(linkId, pacienteNome) {
    const linkElement = document.getElementById(linkId);
    const linkUrl = linkElement.textContent || linkElement.innerText;
    
    const mensagem = encodeURIComponent(`Olá ${pacienteNome}, por favor preencha o formulário de anamnese antes da sua consulta através deste link: ${linkUrl}`);
    const whatsappUrl = `https://wa.me/?text=${mensagem}`;
    
    window.open(whatsappUrl, '_blank');
}

// Função para criar o QR Code do link
function generateQRCode(linkUrl, qrCodeElementId) {
    const qrCodeElement = document.getElementById(qrCodeElementId);
    
    if (qrCodeElement && typeof QRCode !== 'undefined') {
        qrCodeElement.innerHTML = '';
        new QRCode(qrCodeElement, {
            text: linkUrl,
            width: 128,
            height: 128,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });
    }
}