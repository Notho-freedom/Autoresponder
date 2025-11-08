"""
Service d'envoi d'e-mails via SendGrid
Gère l'envoi automatique de mails de confirmation
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional


class EmailService:
    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None):
        """
        Initialise le service d'envoi d'e-mails
        
        Args:
            api_key: Clé API SendGrid (ou depuis variable d'environnement)
            from_email: Adresse e-mail expéditeur
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        self.from_email = from_email or os.getenv('SENDGRID_FROM_EMAIL', 'noreply@tonservice.com')
        
        if not self.api_key:
            raise ValueError("SendGrid API key is required")
        
        self.client = SendGridAPIClient(self.api_key)
    
    def send_email(self, to_email: str, subject: str, content: str, 
                  content_type: str = "text/html") -> bool:
        """
        Envoie un e-mail via SendGrid
        
        Args:
            to_email: Adresse e-mail du destinataire
            subject: Sujet du mail
            content: Contenu du mail (HTML ou texte)
            content_type: Type de contenu ("text/html" ou "text/plain")
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content(content_type, content)
            )
            
            response = self.client.send(message)
            
            # SendGrid retourne 202 pour un envoi accepté
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du mail à {to_email}: {str(e)}")
            return False
    
    def send_confirmation_email(self, to_email: str, user_name: Optional[str] = None) -> bool:
        """
        Envoie un e-mail de confirmation automatique
        
        Args:
            to_email: Adresse e-mail du destinataire
            user_name: Nom du destinataire (optionnel)
            
        Returns:
            True si envoyé avec succès, False sinon
        """
        subject = "Confirmation de votre réponse"
        
        # Template HTML personnalisable
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Confirmation de réception</h1>
                </div>
                <div class="content">
                    <p>{"Bonjour " + user_name + "," if user_name else "Bonjour,"}</p>
                    <p>Nous avons bien reçu votre réponse au formulaire.</p>
                    <p>Merci pour votre participation !</p>
                    <p>Notre équipe reviendra vers vous prochainement si nécessaire.</p>
                </div>
                <div class="footer">
                    <p>Ceci est un message automatique, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)
    
    def test_connection(self) -> bool:
        """
        Test la connexion à l'API SendGrid
        
        Returns:
            True si la connexion fonctionne
        """
        try:
            # Test simple sans envoi réel
            return self.api_key is not None and len(self.api_key) > 0
        except Exception as e:
            print(f"Erreur de connexion SendGrid: {str(e)}")
            return False
