"""
Service d'envoi d'e-mails avec SMTP (Gmail, Outlook, etc.)
Alternative à SendGrid pour l'envoi via serveur SMTP classique
VERSION OPTIMISÉE avec logging et templates centralisés
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from config.constants import ErrorMessages, SuccessMessages, EmailTemplates
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SMTPEmailService:
    """Service d'envoi d'e-mails via SMTP (Gmail, Outlook, etc.)"""
    
    def __init__(self):
        """Initialise le service SMTP avec les variables d'environnement"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '465'))  # 465=SSL, 587=TLS
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('SMTP_FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('SMTP_FROM_NAME', 'Auto-Responder')
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials missing, email service disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(SuccessMessages.SERVICE_INITIALIZED.format(
                service=f"SMTP ({self.smtp_server}:{self.smtp_port}, From: {self.from_email})"
            ))
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        content: str, 
        content_type: str = "html"
    ) -> bool:
        """
        Envoie un e-mail via SMTP
        
        Args:
            to_email: Adresse e-mail du destinataire
            subject: Sujet du mail
            content: Contenu du mail (HTML ou texte)
            content_type: Type de contenu ("html" ou "plain")
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.enabled:
            logger.error(ErrorMessages.EMAIL_SERVICE_FAILED)
            return False
        
        try:
            # Créer le message MIME
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            # Ajouter le contenu
            if content_type == "html":
                message.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                message.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # Connexion et envoi selon le port
            if self.smtp_port == 465:
                # SSL (port 465)
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)
            else:
                # TLS (port 587 ou autre)
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)
            
            logger.info(SuccessMessages.EMAIL_SENT.format(email=to_email, provider="SMTP"))
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return False
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {str(e)}")
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
        Teste la connexion au serveur SMTP
        
        Returns:
            True si la connexion est OK, False sinon
        """
        if not self.enabled:
            return False
        
        try:
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10) as server:
                    server.login(self.smtp_user, self.smtp_password)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
            
            logger.info(f"SMTP connection test successful: {self.smtp_server}:{self.smtp_port}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
