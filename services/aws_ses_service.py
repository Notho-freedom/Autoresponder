"""
Service d'envoi d'e-mails avec AWS SES (Simple Email Service)
Alternative à SendGrid/SMTP pour AWS
VERSION OPTIMISÉE avec logging et templates centralisés
"""
import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError

from config.constants import ErrorMessages, SuccessMessages, EmailTemplates
from utils.logger import setup_logger
from utils.validators import extract_email_username, sanitize_name

logger = setup_logger(__name__)


class AWSSESService:
    """Service d'envoi d'e-mails via AWS SES"""
    
    def __init__(self):
        """Initialise le service AWS SES avec les variables d'environnement"""
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.from_email = os.getenv('AWS_SES_FROM_EMAIL', 'noreply@example.com')
        self.from_name = os.getenv('AWS_SES_FROM_NAME', 'Auto-Responder')
        self.reply_to = os.getenv('AWS_SES_REPLY_TO', self.from_email)
        
        if not self.aws_access_key or not self.aws_secret_key:
            logger.warning("AWS SES credentials missing, email service disabled")
            self.client = None
        else:
            try:
                self.client = boto3.client(
                    'ses',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                )
                logger.info(SuccessMessages.SERVICE_INITIALIZED.format(
                    service=f"AWS SES (Region: {self.aws_region}, From: {self.from_email})"
                ))
            except Exception as e:
                logger.error(f"AWS SES initialization failed: {str(e)}")
                self.client = None
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        content: str, 
        content_type: str = "html"
    ) -> bool:
        """
        Envoie un e-mail via AWS SES
        
        Args:
            to_email: Adresse e-mail du destinataire
            subject: Sujet du mail
            content: Contenu du mail (HTML ou texte)
            content_type: Type de contenu ("html" ou "plain")
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.client:
            logger.error("AWS SES service not initialized")
            return False
        
        try:
            # Construire le message
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'}
            }
            
            if content_type == "html":
                message['Body'] = {
                    'Html': {'Data': content, 'Charset': 'UTF-8'}
                }
            else:
                message['Body'] = {
                    'Text': {'Data': content, 'Charset': 'UTF-8'}
                }
            
            # Envoi via SES
            response = self.client.send_email(
                Source=f"{self.from_name} <{self.from_email}>",
                Destination={'ToAddresses': [to_email]},
                Message=message,
                ReplyToAddresses=[self.reply_to]
            )
            
            if response.get('MessageId'):
                logger.info(SuccessMessages.EMAIL_SENT.format(email=to_email, provider="AWS SES"))
                logger.debug(f"AWS SES MessageId: {response['MessageId']}")
                return True
            else:
                logger.warning(f"AWS SES unexpected response: {response}")
                return False
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            logger.error(f"AWS SES ClientError [{error_code}]: {error_msg}")
            
            # Messages d'erreur spécifiques
            if error_code == 'MessageRejected':
                logger.error("Email rejected - verify email address or domain verification")
            elif error_code == 'MailFromDomainNotVerified':
                logger.error("Domain not verified - go to AWS SES console to verify domain")
            
            return False
            
        except BotoCoreError as e:
            logger.error(f"AWS SES BotoCoreError: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email via AWS SES: {str(e)}")
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
        display_name = sanitize_name(name) if name else extract_email_username(to_email)
        subject = f"Confirmation - Formulaire recu de {display_name}"
        html_content = EmailTemplates.get_confirmation_html(display_name, to_email)
        
        return self.send_email(to_email, subject, html_content, "html")
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à AWS SES
        
        Returns:
            True si la connexion est OK, False sinon
        """
        if not self.client:
            return False
        
        try:
            # Vérifier le quota d'envoi
            response = self.client.get_send_quota()
            max_send = response.get('Max24HourSend', 0)
            sent_last_24h = response.get('SentLast24Hours', 0)
            logger.info(f"AWS SES connection OK - Quota: {sent_last_24h}/{max_send} emails/24h")
            return True
        except Exception as e:
            logger.error(f"AWS SES connection test failed: {str(e)}")
            return False
    
    def get_send_statistics(self) -> dict:
        """
        Récupère les statistiques d'envoi AWS SES
        
        Returns:
            Dict avec Max24HourSend, SentLast24Hours, MaxSendRate
        """
        if not self.client:
            return {"error": "Service not initialized"}
        
        try:
            response = self.client.get_send_quota()
            return {
                "Max24HourSend": response.get('Max24HourSend', 0),
                "SentLast24Hours": response.get('SentLast24Hours', 0),
                "MaxSendRate": response.get('MaxSendRate', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get AWS SES statistics: {str(e)}")
            return {"error": str(e)}
    
    def verify_email_address(self, email: str) -> bool:
        """
        Envoie une demande de vérification d'adresse email
        (Nécessaire en mode sandbox AWS SES)
        
        Args:
            email: Adresse email à vérifier
            
        Returns:
            True si la demande est envoyée, False sinon
        """
        if not self.client:
            return False
        
        try:
            self.client.verify_email_identity(EmailAddress=email)
            logger.info(f"Verification email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False
