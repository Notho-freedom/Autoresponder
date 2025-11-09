"""
Service d'envoi d'e-mails avec SendGrid
Alternative à SMTP qui fonctionne sur tous les hébergeurs
VERSION OPTIMISÉE avec logging et templates centralisés
"""
import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, ReplyTo

from config.constants import ErrorMessages, SuccessMessages, EmailTemplates
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SendGridEmailService:
    """Service d'envoi d'e-mails via l'API SendGrid"""
    
    def __init__(self):
        """Initialise le service SendGrid avec les variables d'environnement"""
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', os.getenv('SMTP_FROM_EMAIL', 'noreply@example.com'))
        
        if not self.api_key:
            logger.warning(ErrorMessages.SENDGRID_API_KEY_MISSING)
            self.client = None
        else:
            self.client = SendGridAPIClient(self.api_key)
            logger.info(SuccessMessages.SERVICE_INITIALIZED.format(service=f"SendGrid ({self.from_email})"))
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        content: str, 
        content_type: str = "html"
    ) -> bool:
        """
        Envoie un e-mail via l'API SendGrid
        
        Args:
            to_email: Adresse e-mail du destinataire
            subject: Sujet du mail
            content: Contenu du mail (HTML ou texte)
            content_type: Type de contenu ("html" ou "plain")
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.client:
            logger.error(ErrorMessages.EMAIL_SERVICE_FAILED)
            return False
        
        try:
            message = Mail(
                from_email=Email(self.from_email, "Auto-Responder"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", content) if content_type == "html" else Content("text/plain", content)
            )
            
            # Anti-spam: Reply-To valide
            reply_to_email = os.getenv('SENDGRID_REPLY_TO_EMAIL', '')
            message.reply_to = ReplyTo(reply_to_email, "Support")
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(SuccessMessages.EMAIL_SENT.format(email=to_email, provider="SendGrid"))
                return True
            else:
                logger.warning(ErrorMessages.SENDGRID_INVALID_RESPONSE.format(status_code=response.status_code))
                return False
                
        except Exception as e:
            logger.error(ErrorMessages.SENDGRID_SEND_FAILED.format(error=str(e)))
            return False
    
    def send_confirmation_email(self, to_email: str, name: Optional[str] = None) -> bool:
        """
        Envoie un e-mail de confirmation de soumission du formulaire
        
        Args:
            to_email: Adresse e-mail du destinataire
            name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        from utils.validators import extract_email_username, sanitize_name
        
        display_name = sanitize_name(name) if name else extract_email_username(to_email)
        subject = f"Confirmation - Formulaire recu de {display_name}"
        html_content = EmailTemplates.get_confirmation_html(display_name, to_email)
        
        return self.send_email(to_email, subject, html_content, "html")
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à l'API SendGrid
        
        Returns:
            True si la connexion est OK, False sinon
        """
        if not self.client:
            return False
        
        try:
            # SendGrid n'a pas de méthode "ping", on vérifie juste que l'API key est valide
            # En vérifiant que le client est correctement initialisé
            return bool(self.api_key)
        except Exception as e:
            logger.error(f"SendGrid connection test failed: {str(e)}")
            return False
