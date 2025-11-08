"""
Factory pour créer l'instance de service Firestore
Utilise uniquement Firestore pour le stockage (pas de JSON local)
"""
import os

from .firestore_service import FirestoreService


def get_database_service() -> FirestoreService:
    """
    Crée et retourne le service Firestore
    
    Les credentials peuvent être fournis via :
    - Variable d'environnement FIREBASE_CREDENTIALS_JSON (production)
    - Fichier firestore-credentials.json (développement)
    
    Returns:
        Instance de FirestoreService
    """
    firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    firebase_creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firestore-credentials.json')
    
    print("🔥 Initialisation de Firestore pour le stockage...")
    
    try:
        if firebase_creds_json:
            return FirestoreService(credentials_json=firebase_creds_json)
        else:
            return FirestoreService(credentials_path=firebase_creds_path)
    except Exception as e:
        raise ValueError(
            f"❌ Erreur lors de l'initialisation de Firestore: {str(e)}\n"
            "Assurez-vous d'avoir configuré FIREBASE_CREDENTIALS_JSON ou firestore-credentials.json"
        )


# Pour faciliter l'import
__all__ = ['get_database_service']
