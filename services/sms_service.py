"""
Service d'envoi de SMS via Twilio
Gère l'envoi automatique de messages SMS
"""
import os
from twilio.rest import Client
from typing import Optional


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
            raise ValueError("Twilio credentials (SID, Token, Phone) are required")
        
        self.client = Client(self.account_sid, self.auth_token)
    
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
            # Normaliser le numéro si nécessaire
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone
            
            message = self.client.messages.create(
                body=content,
                from_=self.phone_number,
                to=to_phone
            )
            
            # Vérifier que le message a été envoyé ou est en cours d'envoi
            return message.sid is not None and message.status in ['queued', 'sent', 'delivered']
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du SMS à {to_phone}: {str(e)}")
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
        # Message court et concis pour SMS
        if user_name:
            content = f"Bonjour {user_name}, nous avons bien reçu votre réponse. Merci !"
        else:
            content = "Nous avons bien reçu votre réponse au formulaire. Merci pour votre participation !"
        
        # Limiter à 160 caractères pour un SMS standard
        if len(content) > 160:
            content = content[:157] + "..."
        
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
            return account.status == 'active'
        except Exception as e:
            print(f"Erreur de connexion Twilio: {str(e)}")
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
            print(f"Erreur lors de la récupération du solde: {str(e)}")
            return None
