"""
Service d'envoi de SMS via Twilio
Gère l'envoi automatique de messages SMS
VERSION OPTIMISÉE avec logging et messages centralisés
"""
import os
from twilio.rest import Client
from typing import Optional

from config.constants import ErrorMessages, SuccessMessages, SMSTemplates, Config
from utils.logger import setup_logger
from utils.validators import normalize_phone

logger = setup_logger(__name__)


class SMSService:
    def __init__(self, account_sid: Optional[str] = None, 
                 auth_token: Optional[str] = None,
                 phone_number: Optional[str] = None):
        """
        Initialise le service d'envoi de SMS
        
        Args:
            account_sid: SID du compte Twilio (ou depuis variable d'environnement)
            auth_token: Token d'authentification Twilio
            phone_number: Numéro de téléphone Twilio expéditeur
        """
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = phone_number or os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.error(ErrorMessages.TWILIO_CREDENTIALS_MISSING)
            raise ValueError(ErrorMessages.TWILIO_CREDENTIALS_MISSING)
        
        self.client = Client(self.account_sid, self.auth_token)
        logger.info(SuccessMessages.SERVICE_INITIALIZED.format(service=f"Twilio ({self.phone_number})"))
    
    def send_sms(self, to_phone: str, content: str) -> bool:
        """
        Envoie un SMS via Twilio
        
        Args:
            to_phone: Numéro de téléphone du destinataire (format international: +237...)
            content: Contenu du SMS (max 160 caractères recommandés)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        try:
            # Normaliser le numéro
            to_phone = normalize_phone(to_phone)
            
            message = self.client.messages.create(
                body=content,
                from_=self.phone_number,
                to=to_phone
            )
            
            # Vérifier que le message a été envoyé ou est en cours d'envoi
            if message.sid and message.status in ['queued', 'sent', 'delivered']:
                logger.info(SuccessMessages.SMS_SENT.format(phone=to_phone))
                return True
            else:
                logger.warning(f"SMS status unexpected: {message.status}")
                return False
            
        except Exception as e:
            logger.error(ErrorMessages.TWILIO_SEND_FAILED.format(error=str(e)))
            return False
    
    def send_confirmation_sms(self, to_phone: str, user_name: Optional[str] = None) -> bool:
        """
        Envoie un SMS de confirmation automatique
        
        Args:
            to_phone: Numéro de téléphone du destinataire
            user_name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        from utils.validators import sanitize_name
        
        # Nettoyer le nom si fourni
        clean_name = sanitize_name(user_name) if user_name else None
        
        # Générer le message
        content = SMSTemplates.get_confirmation_message(clean_name)
        
        # Tronquer si nécessaire
        content = SMSTemplates.truncate_message(content, Config.SMS_MAX_LENGTH)
        
        return self.send_sms(to_phone, content)
    
    def test_connection(self) -> bool:
        """
        Test la connexion à l'API Twilio
        
        Returns:
            True si la connexion fonctionne
        """
        try:
            # Récupérer les informations du compte pour tester la connexion
            account = self.client.api.accounts(self.account_sid).fetch()
            is_active = account.status == 'active'
            if is_active:
                logger.info(SuccessMessages.SERVICE_HEALTHY.format(service="Twilio"))
            return is_active
        except Exception as e:
            logger.error(ErrorMessages.TWILIO_CONNECTION_FAILED.format(error=str(e)))
            return False
    
    def get_account_balance(self) -> Optional[str]:
        """
        Récupère le solde du compte Twilio
        
        Returns:
            Solde formaté ou None en cas d'erreur
        """
        try:
            balance = self.client.api.accounts(self.account_sid).balance.fetch()
            return f"{balance.balance} {balance.currency}"
        except Exception as e:
            logger.error(f"Failed to get Twilio balance: {str(e)}")
            return None
