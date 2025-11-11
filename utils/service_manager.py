"""
Gestionnaire de services optimisé avec pattern Singleton
Gère l'initialisation et le cycle de vie des services
Version Brevo: Brevo pour emails ET SMS (plateforme unique)
"""
import os
from typing import Optional
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
        
        self._email_service = None
        self._sms_service = None
        self._db_service = None
        self._initialized = True
        
        logger.info("ServiceManager initialized (Brevo Email + SMS)")
    
    @property
    def email_service(self):
        """
        Retourne le service email Brevo (initialisation paresseuse)
        
        Returns:
            Instance du service Brevo
        """
        if self._email_service is None:
            with self._lock:
                if self._email_service is None:
                    try:
                        from services.brevo_email_service import BrevoEmailService
                        self._email_service = BrevoEmailService()
                        logger.info("Email service initialized: Brevo")
                    except Exception as e:
                        logger.error(f"Failed to initialize Brevo service: {e}")
                        raise
        return self._email_service
    
    @property
    def sms_service(self):
        """
        Retourne le service SMS Brevo (initialisation paresseuse)
        
        Returns:
            Instance du service Brevo SMS
        """
        if self._sms_service is None:
            with self._lock:
                if self._sms_service is None:
                    try:
                        from services.brevo_sms_service import BrevoSMSService
                        self._sms_service = BrevoSMSService()
                        logger.info("SMS service initialized: Brevo SMS")
                    except Exception as e:
                        logger.error(f"Failed to initialize Brevo SMS service: {e}")
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
                "email": "Brevo",
                "sms": "Brevo"
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
