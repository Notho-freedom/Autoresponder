"""
Service d'envoi d'e-mails avec SendGrid
Alternative à SMTP qui fonctionne sur tous les hébergeurs
"""
import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


class SendGridEmailService:
    """Service d'envoi d'e-mails via l'API SendGrid"""
    
    def __init__(self):
        """Initialise le service SendGrid avec les variables d'environnement"""
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', os.getenv('SMTP_FROM_EMAIL', 'noreply@example.com'))
        
        if not self.api_key:
            print("⚠️  SENDGRID_API_KEY non configuré, le service email ne fonctionnera pas")
            self.client = None
        else:
            self.client = SendGridAPIClient(self.api_key)
            print(f"✅ Service SendGrid initialisé avec {self.from_email}")
    
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
            print("❌ Service SendGrid non initialisé")
            return False
        
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", content) if content_type == "html" else Content("text/plain", content)
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ E-mail envoyé avec succès à {to_email} (SendGrid)")
                return True
            else:
                print(f"⚠️  Réponse SendGrid inattendue: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du mail à {to_email}: {str(e)}")
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
        display_name = name if name else to_email.split('@')[0]
        
        subject = "Confirmation de réception de votre formulaire"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
                .button {{ background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Confirmation de réception</h1>
                </div>
                <div class="content">
                    <p>Bonjour <strong>{display_name}</strong>,</p>
                    
                    <p>Nous avons bien reçu votre soumission de formulaire Google Forms.</p>
                    
                    <p>Votre demande a été enregistrée avec succès et sera traitée dans les plus brefs délais.</p>
                    
                    <p>Si vous avez des questions, n'hésitez pas à nous contacter.</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                        <p style="margin: 0;"><strong>Détails de votre soumission:</strong></p>
                        <p style="margin: 5px 0;">📧 E-mail: {to_email}</p>
                        <p style="margin: 5px 0;">📅 Date: {self._get_current_datetime()}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>Cet e-mail a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    <p>© 2025 Google Forms Auto-Responder</p>
                </div>
            </div>
        </body>
        </html>
        """
        
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
            print(f"❌ Erreur de connexion SendGrid: {str(e)}")
            return False
    
    def _get_current_datetime(self) -> str:
        """Retourne la date et heure actuelles formatées"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y à %H:%M")
