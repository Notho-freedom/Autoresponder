"""
Service d'envoi d'e-mails via SMTP (Gmail)
Remplace SendGrid pour l'envoi d'e-mails
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


class SMTPEmailService:
    def __init__(
        self, 
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        Initialise le service d'envoi d'e-mails via SMTP
        
        Args:
            smtp_server: Serveur SMTP (ex: smtp.gmail.com)
            smtp_port: Port SMTP (587 pour TLS, 465 pour SSL)
            smtp_user: Nom d'utilisateur SMTP (email)
            smtp_password: Mot de passe SMTP (mot de passe d'application pour Gmail)
            from_email: Adresse e-mail expéditeur
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('SMTP_FROM_EMAIL') or self.smtp_user
        
        if not all([self.smtp_user, self.smtp_password]):
            raise ValueError("SMTP user and password are required")
    
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
        try:
            # Connexion au serveur SMTP
            if self.smtp_port == 465:
                # SSL
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # TLS (port 587)
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            # Authentification
            server.login(self.smtp_user, self.smtp_password)
            
            # Préparation du message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Ajouter le corps du message
            if content_type == "html":
                msg.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # Envoyer l'e-mail
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print(f"❌ Erreur d'authentification SMTP pour {self.smtp_user}")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Erreur SMTP lors de l'envoi à {to_email}: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du mail à {to_email}: {str(e)}")
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
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ padding: 20px; background-color: #f9f9f9; border-radius: 0 0 5px 5px; }}
                .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Confirmation de réception</h1>
                </div>
                <div class="content">
                    <p>{"Bonjour " + user_name + "," if user_name else "Bonjour,"}</p>
                    <p>Nous avons bien reçu votre réponse au formulaire.</p>
                    <p><strong>Merci pour votre participation !</strong></p>
                    <p>Notre équipe reviendra vers vous prochainement si nécessaire.</p>
                </div>
                <div class="footer">
                    <p>Ceci est un message automatique, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content, content_type="html")
    
    def test_connection(self) -> bool:
        """
        Test la connexion au serveur SMTP
        
        Returns:
            True si la connexion fonctionne
        """
        try:
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                server.starttls()
            
            server.login(self.smtp_user, self.smtp_password)
            server.quit()
            return True
            
        except smtplib.SMTPAuthenticationError:
            print(f"❌ Erreur d'authentification SMTP")
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion SMTP: {str(e)}")
            return False
