"""
Service d'envoi de SMS avec AWS SNS (Amazon Simple Notification Service)
Alternative à Twilio pour l'envoi de SMS
VERSION OPTIMISÉE avec logging et templates centralisés
"""
import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError

from config.constants import ErrorMessages, SuccessMessages, SMSTemplates
from utils.logger import setup_logger
from utils.validators import normalize_phone

logger = setup_logger(__name__)


class AWSSNSService:
    """Service d'envoi de SMS via AWS SNS"""
    
    def __init__(self):
        """Initialise le service AWS SNS avec les variables d'environnement"""
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.sender_id = os.getenv('AWS_SNS_SENDER_ID', 'AutoResp')  # Nom affiché (max 11 caractères)
        
        if not self.aws_access_key or not self.aws_secret_key:
            logger.warning("AWS SNS credentials missing, SMS service disabled")
            self.client = None
        else:
            try:
                self.client = boto3.client(
                    'sns',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                )
                logger.info(SuccessMessages.SERVICE_INITIALIZED.format(
                    service=f"AWS SNS (Region: {self.aws_region}, Sender: {self.sender_id})"
                ))
            except Exception as e:
                logger.error(f"AWS SNS initialization failed: {str(e)}")
                self.client = None
    
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Envoie un SMS via AWS SNS
        
        Args:
            phone: Numéro de téléphone (format international: +33...)
            message: Contenu du SMS
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        if not self.client:
            logger.error("AWS SNS service not initialized")
            return False
        
        try:
            # Normaliser le numéro (format E.164: +33...)
            phone = normalize_phone(phone)
            
            # Paramètres de l'envoi SNS
            params = {
                'PhoneNumber': phone,
                'Message': message,
                'MessageAttributes': {
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': self.sender_id
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'  # Prioritaire (pas de marketing)
                    }
                }
            }
            
            response = self.client.publish(**params)
            
            if response.get('MessageId'):
                logger.info(SuccessMessages.SMS_SENT.format(phone=phone))
                logger.debug(f"AWS SNS MessageId: {response['MessageId']}")
                return True
            else:
                logger.warning(f"AWS SNS unexpected response: {response}")
                return False
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            logger.error(f"AWS SNS ClientError [{error_code}]: {error_msg}")
            return False
            
        except BotoCoreError as e:
            logger.error(f"AWS SNS BotoCoreError: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send SMS via AWS SNS: {str(e)}")
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
        Teste la connexion à AWS SNS
        
        Returns:
            True si la connexion est OK, False sinon
        """
        if not self.client:
            return False
        
        try:
            # Vérifier les quotas SMS (GetSMSAttributes)
            response = self.client.get_sms_attributes(attributes=['MonthlySpendLimit'])
            logger.info(f"AWS SNS connection OK - Monthly limit: ${response.get('attributes', {}).get('MonthlySpendLimit', 'N/A')}")
            return True
        except Exception as e:
            logger.error(f"AWS SNS connection test failed: {str(e)}")
            return False
    
    def get_monthly_spend(self) -> dict:
        """
        Récupère les statistiques de dépenses SMS AWS SNS
        
        Returns:
            Dict avec MonthlySpendLimit et dépenses actuelles
        """
        if not self.client:
            return {"error": "Service not initialized"}
        
        try:
            response = self.client.get_sms_attributes()
            return response.get('attributes', {})
        except Exception as e:
            logger.error(f"Failed to get AWS SNS spend info: {str(e)}")
            return {"error": str(e)}
