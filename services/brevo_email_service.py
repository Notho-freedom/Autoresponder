"""
Service d'envoi d'e-mails via Brevo (anciennement Sendinblue)
Supporte à la fois l'API REST et SMTP
VERSION OPTIMISÉE avec logging et templates centralisés
"""
import os
from typing import Optional
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.constants import ErrorMessages, SuccessMessages, EmailTemplates
from utils.logger import setup_logger
from utils.validators import sanitize_name

logger = setup_logger(__name__)


class BrevoEmailService:
    """Service d'envoi d'emails via Brevo (API + SMTP)"""
    
    def __init__(self):
        """Initialise le service Brevo avec les variables d'environnement"""
        # API REST
        self.api_key = os.getenv('BREVO_API_KEY')
        self.api_url = "https://api.brevo.com/v3/smtp/email"
        
        # SMTP
        self.smtp_server = os.getenv('BREVO_SMTP_SERVER', 'smtp-relay.brevo.com')
        self.smtp_port = int(os.getenv('BREVO_SMTP_PORT', '587'))
        self.smtp_login = os.getenv('BREVO_SMTP_LOGIN')
        self.smtp_password = os.getenv('BREVO_SMTP_PASSWORD')
        
        # Configuration email
        self.from_email = os.getenv('BREVO_FROM_EMAIL', 'no-reply@nkenganalytics.ora-research.com')
        self.from_name = os.getenv('BREVO_FROM_NAME', 'Nkeng Analytics')
        self.reply_to = os.getenv('BREVO_REPLY_TO', 'contact@nkenganalytics.com')
        
        # Mode d'envoi préféré (api ou smtp)
        self.preferred_mode = os.getenv('BREVO_MODE', 'api')
        
        if not self.api_key and not (self.smtp_login and self.smtp_password):
            logger.warning("Brevo credentials missing, email service disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(SuccessMessages.SERVICE_INITIALIZED.format(
                service=f"Brevo Email (Mode: {self.preferred_mode}, From: {self.from_email})"
            ))
    
    def send_email_api(self, to_email: str, subject: str, html_content: str, 
                       to_name: Optional[str] = None) -> bool:
        """
        Envoie un email via l'API REST Brevo
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
            to_name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.api_key:
            logger.error("Brevo API key not configured")
            return False
        
        try:
            headers = {
                'api-key': self.api_key,
                'Content-Type': 'application/json',
                'accept': 'application/json'
            }
            
            payload = {
                'sender': {
                    'name': self.from_name,
                    'email': self.from_email
                },
                'to': [
                    {
                        'email': to_email,
                        'name': to_name or to_email.split('@')[0]
                    }
                ],
                'subject': subject,
                'htmlContent': html_content,
                'replyTo': {
                    'email': self.reply_to
                }
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get('messageId')
            
            if message_id:
                logger.info(f"Email sent successfully to {to_email} via Brevo API")
                logger.debug(f"Brevo MessageId: {message_id}")
                return True
            else:
                logger.warning(f"Brevo unexpected response: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Brevo API request failed: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email via Brevo API: {str(e)}")
            return False
    
    def send_email_smtp(self, to_email: str, subject: str, html_content: str,
                        to_name: Optional[str] = None) -> bool:
        """
        Envoie un email via SMTP Brevo
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
            to_name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not (self.smtp_login and self.smtp_password):
            logger.error("Brevo SMTP credentials not configured")
            return False
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = f"{to_name or to_email.split('@')[0]} <{to_email}>"
            msg['Subject'] = subject
            msg['Reply-To'] = self.reply_to
            
            # Ajouter le contenu HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connexion SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_login, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email} via Brevo SMTP")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"Brevo SMTP error: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email via Brevo SMTP: {str(e)}")
            return False
    
    def send_email(self, to_email: str, subject: str, html_content: str,
                   to_name: Optional[str] = None) -> bool:
        """
        Envoie un email via Brevo (choisit automatiquement API ou SMTP)
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
            to_name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.enabled:
            logger.error("Brevo service not initialized")
            return False
        
        # Essayer le mode préféré en premier
        if self.preferred_mode == 'api' and self.api_key:
            return self.send_email_api(to_email, subject, html_content, to_name)
        elif self.preferred_mode == 'smtp' and self.smtp_login:
            return self.send_email_smtp(to_email, subject, html_content, to_name)
        
        # Fallback: essayer l'autre mode
        if self.api_key:
            logger.info("Trying Brevo API as fallback")
            return self.send_email_api(to_email, subject, html_content, to_name)
        elif self.smtp_login:
            logger.info("Trying Brevo SMTP as fallback")
            return self.send_email_smtp(to_email, subject, html_content, to_name)
        
        logger.error("No Brevo method available")
        return False
    
    def send_confirmation_email(self, to_email: str, name: Optional[str] = None) -> bool:
        """
        Envoie un email de confirmation de soumission du formulaire
        
        Args:
            to_email: Adresse email du destinataire
            name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        display_name = sanitize_name(name) if name else "Utilisateur"
        subject = f"Confirmation de votre soumission - {display_name}"
        html_content = EmailTemplates.get_confirmation_html(display_name, to_email)
        
        return self.send_email(to_email, subject, html_content, display_name)
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à Brevo (API ou SMTP)
        
        Returns:
            True si la connexion est OK, False sinon
        """
        if not self.enabled:
            return False
        
        # Tester l'API
        if self.api_key:
            try:
                headers = {
                    'api-key': self.api_key,
                    'accept': 'application/json'
                }
                response = requests.get('https://api.brevo.com/v3/account', 
                                       headers=headers, timeout=10)
                response.raise_for_status()
                
                account = response.json()
                logger.info(f"Brevo API connection OK - Email: {account.get('email', 'N/A')}")
                return True
                
            except Exception as e:
                logger.error(f"Brevo API connection test failed: {str(e)}")
        
        # Tester SMTP en fallback
        if self.smtp_login and self.smtp_password:
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.smtp_login, self.smtp_password)
                
                logger.info(f"Brevo SMTP connection OK - Login: {self.smtp_login}")
                return True
                
            except Exception as e:
                logger.error(f"Brevo SMTP connection test failed: {str(e)}")
        
        return False
    
    def get_account_info(self) -> dict:
        """
        Récupère les informations du compte Brevo
        
        Returns:
            Dict avec les infos du compte
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        try:
            headers = {
                'api-key': self.api_key,
                'accept': 'application/json'
            }
            response = requests.get('https://api.brevo.com/v3/account', 
                                   headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get Brevo account info: {str(e)}")
            return {"error": str(e)}
