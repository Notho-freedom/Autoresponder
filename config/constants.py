"""
Configuration et constantes centralisées
Tous les messages, templates et configurations sont définis ici
"""
from datetime import datetime


# ============= CONFIGURATION =============
class Config:
    """Configuration globale de l'application"""
    APP_NAME = "Google Forms Auto-Responder"
    APP_VERSION = "1.0.0"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # secondes
    SMS_MAX_LENGTH = 160
    STATS_CACHE_TTL = 300  # 5 minutes


# ============= MESSAGES D'ERREUR =============
class ErrorMessages:
    """Messages d'erreur centralisés"""
    # Authentification
    UNAUTHORIZED = "Unauthorized: Invalid or missing secret key"
    MISSING_AUTH_HEADER = "Missing Authorization header"
    INVALID_AUTH_FORMAT = "Invalid Authorization format. Use: Bearer <token>"
    
    # Validation
    MISSING_REQUIRED_FIELDS = "Missing required fields: {fields}"
    INVALID_EMAIL = "Invalid email format: {email}"
    INVALID_PHONE = "Invalid phone format: {phone}"
    
    # Services
    SERVICE_UNAVAILABLE = "Service temporarily unavailable: {service}"
    EMAIL_SERVICE_FAILED = "Email service initialization failed"
    SMS_SERVICE_FAILED = "SMS service initialization failed"
    FIRESTORE_CONNECTION_FAILED = "Firestore connection failed: {error}"
    
    # Traitement
    ALREADY_PROCESSED = "This response has already been processed"
    PROCESSING_FAILED = "Failed to process form response: {error}"
    
    # SendGrid
    SENDGRID_API_KEY_MISSING = "SENDGRID_API_KEY not configured, email service disabled"
    SENDGRID_SEND_FAILED = "Failed to send email via SendGrid: {error}"
    SENDGRID_INVALID_RESPONSE = "Unexpected SendGrid response: {status_code}"
    
    # Twilio
    TWILIO_CREDENTIALS_MISSING = "Twilio credentials (SID, Token, Phone) are required"
    TWILIO_SEND_FAILED = "Failed to send SMS via Twilio: {error}"
    TWILIO_CONNECTION_FAILED = "Twilio connection test failed: {error}"
    
    # Firestore
    FIRESTORE_INIT_FAILED = "Firestore initialization failed: {error}"
    FIRESTORE_QUERY_FAILED = "Firestore query failed: {error}"
    FIRESTORE_WRITE_FAILED = "Failed to write to Firestore: {error}"
    FIRESTORE_DELETE_FAILED = "Failed to delete from Firestore: {error}"


# ============= MESSAGES DE SUCCÈS =============
class SuccessMessages:
    """Messages de succès centralisés"""
    # Email
    EMAIL_SENT = "Email sent successfully to {email} via {provider}"
    EMAIL_QUEUED = "Email queued for delivery to {email}"
    
    # SMS
    SMS_SENT = "SMS sent successfully to {phone}"
    SMS_QUEUED = "SMS queued for delivery to {phone}"
    
    # Services
    SERVICE_INITIALIZED = "Service initialized: {service}"
    SERVICE_HEALTHY = "Service health check passed: {service}"
    
    # Traitement
    RESPONSE_PROCESSED = "Form response processed successfully"
    RESPONSE_RECORDED = "Response recorded in database: {response_id}"
    
    # Base de données
    DATA_SAVED = "Data saved successfully"
    DATA_RETRIEVED = "Data retrieved: {count} records"


# ============= MESSAGES D'INFO =============
class InfoMessages:
    """Messages informatifs centralisés"""
    STARTUP = ">> Starting {app_name} v{version}..."
    SHUTDOWN = ">> Shutting down {app_name}..."
    SERVICE_READY = ">> All services initialized and ready"
    PROCESSING_REQUEST = "Processing form submission from {email}"
    DUPLICATE_DETECTED = "Duplicate submission detected: {response_id}"
    PARTIAL_SUCCESS = "Partial success: Email={email_ok}, SMS={sms_ok}"
    RESPONSE_PROCESSED = "Form response processed successfully"


# ============= TEMPLATES EMAIL =============
class EmailTemplates:
    """Templates d'emails HTML"""
    
    @staticmethod
    def get_confirmation_html(display_name: str, email: str) -> str:
        """Template de confirmation de soumission"""
        timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; 
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 20px auto; 
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .content {{ 
                    padding: 30px;
                    background-color: #ffffff;
                }}
                .content p {{
                    margin: 15px 0;
                    color: #555;
                }}
                .highlight {{
                    background-color: #f0f8f0;
                    border-left: 4px solid #4CAF50;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .details {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }}
                .details p {{
                    margin: 8px 0;
                    font-size: 14px;
                }}
                .footer {{ 
                    text-align: center; 
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-top: 1px solid #e0e0e0;
                }}
                .footer p {{
                    margin: 5px 0;
                    font-size: 12px;
                    color: #999;
                }}
                .icon {{
                    font-size: 20px;
                    margin-right: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Confirmation de réception</h1>
                </div>
                <div class="content">
                    <p>Bonjour <strong>{display_name}</strong>,</p>
                    
                    <div class="highlight">
                        <p style="margin: 0;">
                            <strong>🎉 Votre formulaire a été enregistré avec succès !</strong>
                        </p>
                    </div>
                    
                    <p>Nous avons bien reçu votre soumission et elle sera traitée dans les plus brefs délais.</p>
                    
                    <p>Notre équipe examinera votre demande et vous contactera si nécessaire.</p>
                    
                    <div class="details">
                        <p><strong>📋 Détails de votre soumission:</strong></p>
                        <p><span class="icon">📧</span> E-mail: {email}</p>
                        <p><span class="icon">📅</span> Date: {timestamp}</p>
                        <p><span class="icon">✓</span> Statut: Confirmé</p>
                    </div>
                    
                    <p style="margin-top: 30px; font-size: 14px; color: #666;">
                        Si vous avez des questions concernant votre soumission, n'hésitez pas à nous contacter.
                    </p>
                </div>
                <div class="footer">
                    <p>Cet e-mail a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    <p>© {datetime.now().year} Google Forms Auto-Responder - Tous droits réservés</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def get_error_notification_html(error_type: str, error_details: str) -> str:
        """Template de notification d'erreur (pour les admins)"""
        timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #fff3f3; padding: 30px; border-radius: 0 0 5px 5px; border: 2px solid #f44336; }}
                .error-box {{ background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 15px 0; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Erreur Système</h1>
                </div>
                <div class="content">
                    <div class="error-box">
                        <p><strong>Type d'erreur:</strong> {error_type}</p>
                        <p><strong>Date:</strong> {timestamp}</p>
                    </div>
                    
                    <p><strong>Détails:</strong></p>
                    <pre>{error_details}</pre>
                    
                    <p style="margin-top: 20px; color: #666;">
                        Veuillez vérifier les logs du serveur pour plus d'informations.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """


# ============= TEMPLATES SMS =============
class SMSTemplates:
    """Templates de SMS"""
    
    @staticmethod
    def get_confirmation_message(name: str = None) -> str:
        """Message de confirmation SMS"""
        if name:
            return f"Bonjour {name}, nous avons bien reçu votre formulaire. Merci pour votre participation !"
        return "Nous avons bien reçu votre réponse au formulaire. Merci pour votre participation !"
    
    @staticmethod
    def get_short_confirmation() -> str:
        """Message de confirmation court (économie de SMS)"""
        return "✅ Formulaire reçu avec succès. Merci !"
    
    @staticmethod
    def truncate_message(message: str, max_length: int = 160) -> str:
        """Tronque un message SMS à la longueur maximale"""
        if len(message) <= max_length:
            return message
        return message[:max_length - 3] + "..."


# ============= RÉPONSES API =============
class APIResponses:
    """Réponses standardisées pour l'API"""
    
    @staticmethod
    def success(data: dict = None, message: str = None) -> dict:
        """Réponse de succès standard"""
        response = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        if message:
            response["message"] = message
        if data:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message: str, code: str = None, details: dict = None) -> dict:
        """Réponse d'erreur standard"""
        response = {
            "status": "error",
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        if code:
            response["code"] = code
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def partial_success(successes: dict, failures: dict) -> dict:
        """Réponse de succès partiel"""
        return {
            "status": "partial",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "successes": successes,
            "failures": failures
        }


# ============= STATUS CODES =============
class StatusCodes:
    """Codes de statut HTTP personnalisés"""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    PARTIAL_SUCCESS = 207
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503
