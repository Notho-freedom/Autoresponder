"""
Service d'envoi de SMS avec Vonage (anciennement Nexmo)
Alternative à AWS SNS pour l'envoi de SMS
VERSION OPTIMISÉE avec logging et templates centralisés
"""
import os
from typing import Optional
import requests

from config.constants import ErrorMessages, SuccessMessages, SMSTemplates
from utils.logger import setup_logger
from utils.validators import normalize_phone

logger = setup_logger(__name__)


class VonageSMSService:
    """Service d'envoi de SMS via Vonage API"""
    
    def __init__(self):
        """Initialise le service Vonage avec les variables d'environnement"""
        self.api_key = os.getenv('VONAGE_API_KEY')
        self.api_secret = os.getenv('VONAGE_API_SECRET')
        self.from_number = os.getenv('VONAGE_FROM_NUMBER', 'Autoresponder')
        self.base_url = "https://rest.nexmo.com/sms/json"
        
        if not self.api_key or not self.api_secret:
            logger.warning("Vonage credentials missing, SMS service disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(SuccessMessages.SERVICE_INITIALIZED.format(
                service=f"Vonage SMS (From: {self.from_number})"
            ))
    
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Envoie un SMS via Vonage
        
        Args:
            phone: Numéro de téléphone (format international: +33...)
            message: Contenu du SMS
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.enabled:
            logger.error("Vonage service not initialized")
            return False
        
        try:
            # Normaliser le numéro (format E.164: +33...)
            phone = normalize_phone(phone)
            
            # Payload pour l'API Vonage
            payload = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'to': phone,
                'from': self.from_number,
                'text': message,
                'type': 'unicode'  # Support des caractères spéciaux
            }
            
            response = requests.post(self.base_url, data=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # Vonage retourne un array de messages
            if result.get('messages'):
                msg_status = result['messages'][0]
                if msg_status.get('status') == '0':  # 0 = success
                    logger.info(SuccessMessages.SMS_SENT.format(phone=phone))
                    logger.debug(f"Vonage MessageId: {msg_status.get('message-id')}")
                    return True
                else:
                    error_text = msg_status.get('error-text', 'Unknown error')
                    logger.error(f"Vonage error [{msg_status.get('status')}]: {error_text}")
                    return False
            else:
                logger.warning(f"Vonage unexpected response: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Vonage API request failed: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send SMS via Vonage: {str(e)}")
            return False
    
    def send_confirmation_sms(self, phone: str, name: Optional[str] = None) -> bool:
        """
        Envoie un SMS de confirmation de soumission du formulaire
        
        Args:
            phone: Numéro de téléphone du destinataire
            name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        from utils.validators import sanitize_name
        
        display_name = sanitize_name(name) if name else "Utilisateur"
        message = SMSTemplates.get_confirmation_message(display_name)
        
        return self.send_sms(phone, message)
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à Vonage en vérifiant le solde du compte
        
        Returns:
            True si la connexion est OK, False sinon
        """
        if not self.enabled:
            return False
        
        try:
            balance_url = f"https://rest.nexmo.com/account/get-balance?api_key={self.api_key}&api_secret={self.api_secret}"
            response = requests.get(balance_url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            balance = result.get('value', 'N/A')
            logger.info(f"Vonage connection OK - Balance: €{balance}")
            return True
            
        except Exception as e:
            logger.error(f"Vonage connection test failed: {str(e)}")
            return False
    
    def get_balance(self) -> dict:
        """
        Récupère le solde du compte Vonage
        
        Returns:
            Dict avec value (balance) et autoReload (bool)
        """
        if not self.enabled:
            return {"error": "Service not initialized"}
        
        try:
            balance_url = f"https://rest.nexmo.com/account/get-balance?api_key={self.api_key}&api_secret={self.api_secret}"
            response = requests.get(balance_url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get Vonage balance: {str(e)}")
            return {"error": str(e)}
