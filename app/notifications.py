import os
import logging
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

# Configure logging
logger = logging.getLogger(__name__)

# Get API keys from environment variables
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@clinicaodontologica.com')

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

def send_email(to_email, subject, html_content, text_content=None):
    """
    Send an email using SendGrid API
    """
    if not SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not set. Email not sent.")
        return False
    
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=text_content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        # Check if status code is in the 2xx range (success)
        status_code = getattr(response, 'status_code', 0)
        if 200 <= status_code < 300:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Failed to send email. Status code: {status_code}")
            return False
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def send_formulario_email(paciente_nome, paciente_email, token_url):
    """
    Send form link email to patient
    """
    subject = "Formulário de Pré-Consulta - Clínica Odontológica"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Olá, {paciente_nome}!</h2>
        <p>Você tem uma consulta agendada na nossa clínica odontológica.</p>
        <p>Por favor, preencha o formulário de pré-consulta clicando no link abaixo:</p>
        <p><a href="{token_url}" style="display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Preencher Formulário</a></p>
        <p>Este link é pessoal e expira em 7 dias.</p>
        <p>Se você não solicitou este formulário, por favor ignore este email.</p>
        <p>Atenciosamente,<br>Equipe da Clínica Odontológica</p>
    </div>
    """
    
    text_content = f"""
    Olá, {paciente_nome}!
    
    Você tem uma consulta agendada na nossa clínica odontológica.
    Por favor, preencha o formulário de pré-consulta acessando o link:
    {token_url}
    
    Este link é pessoal e expira em 7 dias.
    Se você não solicitou este formulário, por favor ignore este email.
    
    Atenciosamente,
    Equipe da Clínica Odontológica
    """
    
    return send_email(paciente_email, subject, html_content, text_content)

def send_lembrete_consulta_sms(telefone, paciente_nome, data_consulta, hora_consulta):
    """
    Send appointment reminder via SMS using Twilio
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials not set. SMS not sent.")
        return False
    
    try:
        # Format phone number to E.164 format if needed
        if telefone and not telefone.startswith('+'):
            # Assuming Brazilian numbers by default (+55)
            telefone = '+55' + re.sub(r'[^0-9]', '', telefone)
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_body = f"Olá {paciente_nome}, lembramos que você tem uma consulta agendada para o dia {data_consulta} às {hora_consulta}. Clínica Odontológica."
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=telefone
        )
        
        logger.info(f"SMS sent with SID: {message.sid}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return False
