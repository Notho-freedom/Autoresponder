"""
Gestionnaire de services optimisé avec pattern Singleton
Gère l'initialisation et le cycle de vie des services
Support multi-providers: SendGrid/SMTP pour emails, Twilio/AWS SNS pour SMS
"""
import os
from typing import Optional, Union
from threading import Lock

from utils.logger import setup_logger

logger = setup_logger(__name__)


class ServiceManager:
    """
    Singleton pour gérer tous les services de l'application
    Lazy loading et réutilisation des instances
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialisation paresseuse - ne crée les services que si nécessaire"""
        if self._initialized:
            return
        
        self._email_service: Optional[Union[SendGridEmailService, SMTPEmailService]] = None
        self._sms_service: Optional[Union[SMSService, AWSSNSService]] = None
        self._db_service = None
        
        # Lire les providers depuis .env
        self._email_provider = os.getenv('EMAIL_PROVIDER', 'sendgrid').lower()
        self._sms_provider = os.getenv('SMS_PROVIDER', 'twilio').lower()
        
        # Validation: au moins un provider doit être configuré
        if self._email_provider not in ['sendgrid', 'smtp']:
            logger.warning(f"Invalid EMAIL_PROVIDER '{self._email_provider}', defaulting to 'sendgrid'")
            self._email_provider = 'sendgrid'
        
        if self._sms_provider not in ['twilio', 'sns']:
            logger.warning(f"Invalid SMS_PROVIDER '{self._sms_provider}', defaulting to 'twilio'")
            self._sms_provider = 'twilio'
        
        self._initialized = True
        logger.info(f"ServiceManager initialized (Email: {self._email_provider}, SMS: {self._sms_provider})")
    
    @property
    def email_service(self):
        """
        Retourne le service email selon le provider configuré (initialisation paresseuse)
        
        Returns:
            Instance du service email (SendGrid ou SMTP)
        """
        if self._email_service is None:
            with self._lock:
                if self._email_service is None:
                    try:
                        if self._email_provider == 'smtp':
                            from services.smtp_email_service import SMTPEmailService
                            self._email_service = SMTPEmailService()
                            logger.info("Email service initialized: SMTP")
                        else:
                            from services.sendgrid_email_service import SendGridEmailService
                            self._email_service = SendGridEmailService()
                            logger.info("Email service initialized: SendGrid")
                    except Exception as e:
                        logger.error(f"Failed to initialize email service ({self._email_provider}): {e}")
                        raise
        return self._email_service
    
    @property
    def sms_service(self):
        """
        Retourne le service SMS selon le provider configuré (initialisation paresseuse)
        
        Returns:
            Instance du service SMS (Twilio ou AWS SNS)
        """
        if self._sms_service is None:
            with self._lock:
                if self._sms_service is None:
                    try:
                        if self._sms_provider == 'sns':
                            from services.aws_sns_service import AWSSNSService
                            self._sms_service = AWSSNSService()
                            logger.info("SMS service initialized: AWS SNS")
                        else:
                            from services.sms_service import SMSService
                            self._sms_service = SMSService()
                            logger.info("SMS service initialized: Twilio")
                    except Exception as e:
                        logger.error(f"Failed to initialize SMS service ({self._sms_provider}): {e}")
                        raise
        return self._sms_service
    
    @property
    def db_service(self):
        """
        Retourne le service de base de données (initialisation paresseuse)
        
        Returns:
            Instance du service de base de données
        """
        if self._db_service is None:
            with self._lock:
                if self._db_service is None:
                    try:
                        from services.db_factory import get_database_service
                        self._db_service = get_database_service()
                        logger.info("Database service initialized")
                    except Exception as e:
                        logger.error(f"Failed to initialize database service: {e}")
                        raise
        return self._db_service
    
    def health_check(self) -> dict:
        """
        Vérifie la santé de tous les services initialisés
        
        Returns:
            Dictionnaire avec le statut de chaque service
        """
        health_status = {
            "email": False,
            "sms": False,
            "database": False
        }
        
        # Vérifier email (si initialisé)
        if self._email_service is not None:
            try:
                health_status["email"] = self._email_service.test_connection()
            except Exception as e:
                logger.warning(f"Email service health check failed: {e}")
        
        # Vérifier SMS (si initialisé)
        if self._sms_service is not None:
            try:
                health_status["sms"] = self._sms_service.test_connection()
            except Exception as e:
                logger.warning(f"SMS service health check failed: {e}")
        
        # Base de données toujours disponible (Firestore)
        health_status["database"] = True
        
        return health_status
    
    def reset(self):
        """
        Réinitialise tous les services (utile pour les tests)
        """
        with self._lock:
            self._email_service = None
            self._sms_service = None
            self._db_service = None
            logger.info("All services reset")
    
    def get_stats(self) -> dict:
        """
        Récupère les statistiques de tous les services
        
        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {
            "providers": {
                "email": self._email_provider,
                "sms": self._sms_provider
            },
            "services_initialized": {
                "email": self._email_service is not None,
                "sms": self._sms_service is not None,
                "database": self._db_service is not None
            }
        }
        
        # Stats de la base de données
        if self._db_service is not None:
            try:
                stats["database"] = self.db_service.get_stats()
            except Exception as e:
                logger.error(f"Failed to get database stats: {e}")
                stats["database"] = {"error": str(e)}
        
        return stats


# Instance globale singleton
service_manager = ServiceManager()
