"""
Service d'envoi de SMS via Brevo (anciennement Sendinblue)
Permet l'envoi de SMS via l'API REST Brevo
VERSION OPTIMISÉE avec logging et templates centralisés
"""
import os
from typing import Optional
import requests

from config.constants import ErrorMessages, SuccessMessages, SMSTemplates
from utils.logger import setup_logger
from utils.validators import normalize_phone

logger = setup_logger(__name__)


class BrevoSMSService:
    """Service d'envoi de SMS via Brevo API"""
    
    def __init__(self):
        """Initialise le service Brevo SMS avec les variables d'environnement"""
        self.api_key = os.getenv('BREVO_API_KEY')
        self.api_url = "https://api.brevo.com/v3/transactionalSMS/sms"
        self.sender = os.getenv('BREVO_SMS_SENDER', 'Brevo')
        
        if not self.api_key:
            logger.warning("Brevo API key missing, SMS service disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(SuccessMessages.SERVICE_INITIALIZED.format(
                service=f"Brevo SMS (Sender: {self.sender})"
            ))
    
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Envoie un SMS via Brevo API
        
        Args:
            phone: Numéro de téléphone (format international: +33...)
            message: Contenu du SMS
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.enabled:
            logger.error("Brevo SMS service not initialized")
            return False
        
        try:
            # Normaliser le numéro (format E.164: +33...)
            phone = normalize_phone(phone)
            
            headers = {
                'api-key': self.api_key,
                'Content-Type': 'application/json',
                'accept': 'application/json'
            }
            
            payload = {
                'sender': self.sender,
                'recipient': phone,
                'content': message,
                'type': 'transactional'  # SMS transactionnel (pas marketing)
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get('messageId') or result.get('reference')
            
            if message_id:
                logger.info(f"SMS sent successfully to {phone}")
                logger.debug(f"Brevo SMS MessageId: {message_id}")
                return True
            else:
                logger.warning(f"Brevo SMS unexpected response: {result}")
                return False
                
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response.text else str(e)
            logger.error(f"Brevo SMS API error: {error_detail}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Brevo SMS request failed: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send SMS via Brevo: {str(e)}")
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
        Teste la connexion à Brevo SMS en vérifiant le compte
        
        Returns:
            True si la connexion est OK, False sinon
        """
        if not self.enabled:
            return False
        
        try:
            headers = {
                'api-key': self.api_key,
                'accept': 'application/json'
            }
            
            # Vérifier l'accès au compte
            response = requests.get('https://api.brevo.com/v3/account', 
                                   headers=headers, timeout=10)
            response.raise_for_status()
            
            account = response.json()
            logger.info(f"Brevo SMS connection OK - Email: {account.get('email', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"Brevo SMS connection test failed: {str(e)}")
            return False
    
    def get_credits(self) -> dict:
        """
        Récupère les crédits SMS disponibles
        
        Returns:
            Dict avec les informations de crédit
        """
        if not self.enabled:
            return {"error": "Service not initialized"}
        
        try:
            headers = {
                'api-key': self.api_key,
                'accept': 'application/json'
            }
            
            # Récupérer les infos du compte
            response = requests.get('https://api.brevo.com/v3/account', 
                                   headers=headers, timeout=10)
            response.raise_for_status()
            
            account = response.json()
            
            # Extraire les crédits SMS
            plan = account.get('plan', [{}])
            if isinstance(plan, list) and len(plan) > 0:
                plan_info = plan[0]
                return {
                    'credits': plan_info.get('credits'),
                    'creditsType': plan_info.get('creditsType')
                }
            
            return account
            
        except Exception as e:
            logger.error(f"Failed to get Brevo SMS credits: {str(e)}")
            return {"error": str(e)}
