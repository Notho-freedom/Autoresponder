"""
Service de gestion de la base de données Firestore
Gère l'enregistrement et la vérification des réponses déjà traitées
Compatible avec le déploiement cloud (Render, Railway, etc.)
"""
import os
import json
from datetime import datetime
from typing import Optional, List, Dict

import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreService:
    def __init__(self, credentials_path: Optional[str] = None, credentials_json: Optional[str] = None):
        """
        Initialise la connexion à Firestore
        
        Args:
            credentials_path: Chemin vers le fichier credentials JSON
            credentials_json: JSON credentials en string (pour variables d'environnement)
        """
        self.collection_name = "responses"
        
        # Initialiser Firebase si pas déjà fait
        if not firebase_admin._apps:
            try:
                if credentials_json:
                    # Depuis variable d'environnement (production)
                    cred_dict = json.loads(credentials_json)
                    cred = credentials.Certificate(cred_dict)
                elif credentials_path and os.path.exists(credentials_path):
                    # Depuis fichier local (développement)
                    cred = credentials.Certificate(credentials_path)
                else:
                    # Essayer les credentials par défaut de l'environnement
                    cred = credentials.ApplicationDefault()
                
                firebase_admin.initialize_app(cred)
            except Exception as e:
                raise ValueError(f"Erreur d'initialisation Firestore: {str(e)}")
        
        self.db = firestore.client()
        self.collection = self.db.collection(self.collection_name)
    
    def already_sent(self, response_id: str) -> bool:
        """
        Vérifie si une réponse a déjà été traitée
        
        Args:
            response_id: Identifiant unique de la réponse
            
        Returns:
            True si déjà envoyé, False sinon
        """
        try:
            doc = self.collection.document(response_id).get()
            return doc.exists
        except Exception as e:
            print(f"Erreur lors de la vérification: {str(e)}")
            return False
    
    def add_response(self, response_id: str, email: str, phone: str, 
                    sent_mail: bool = True, sent_sms: bool = True) -> bool:
        """
        Ajoute une nouvelle réponse traitée dans Firestore
        
        Args:
            response_id: Identifiant unique de la réponse
            email: Adresse e-mail du répondant
            phone: Numéro de téléphone du répondant
            sent_mail: Statut d'envoi du mail
            sent_sms: Statut d'envoi du SMS
            
        Returns:
            True si ajouté avec succès, False si déjà existant
        """
        if self.already_sent(response_id):
            return False
        
        try:
            doc_data = {
                "responseId": response_id,
                "email": email,
                "phone": phone,
                "sent_mail": sent_mail,
                "sent_sms": sent_sms,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            self.collection.document(response_id).set(doc_data)
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'ajout: {str(e)}")
            return False
    
    def get_response(self, response_id: str) -> Optional[Dict]:
        """
        Récupère une réponse spécifique par son ID
        
        Args:
            response_id: Identifiant unique de la réponse
            
        Returns:
            Les données de la réponse ou None si non trouvée
        """
        try:
            doc = self.collection.document(response_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération: {str(e)}")
            return None
    
    def get_all_responses(self, limit: int = 100) -> List[Dict]:
        """
        Récupère toutes les réponses enregistrées
        
        Args:
            limit: Nombre maximum de résultats à retourner
            
        Returns:
            Liste des réponses
        """
        try:
            docs = self.collection.limit(limit).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Erreur lors de la récupération: {str(e)}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Génère des statistiques sur les envois
        
        Returns:
            Dictionnaire avec les statistiques
        """
        try:
            # Compter tous les documents
            docs = self.collection.stream()
            
            total = 0
            mails_sent = 0
            sms_sent = 0
            
            for doc in docs:
                data = doc.to_dict()
                total += 1
                if data.get('sent_mail', False):
                    mails_sent += 1
                if data.get('sent_sms', False):
                    sms_sent += 1
            
            return {
                "total_responses": total,
                "mails_sent": mails_sent,
                "sms_sent": sms_sent,
                "success_rate": 100 if total == 0 else round((mails_sent + sms_sent) / (total * 2) * 100, 2)
            }
            
        except Exception as e:
            print(f"Erreur lors du calcul des stats: {str(e)}")
            return {
                "total_responses": 0,
                "mails_sent": 0,
                "sms_sent": 0,
                "success_rate": 0
            }
    
    def delete_response(self, response_id: str) -> bool:
        """
        Supprime une réponse (utile pour les tests)
        
        Args:
            response_id: Identifiant de la réponse à supprimer
            
        Returns:
            True si supprimé avec succès
        """
        try:
            self.collection.document(response_id).delete()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """
        Supprime toutes les réponses (ATTENTION: action irréversible!)
        Utiliser uniquement pour les tests
        
        Returns:
            True si réussi
        """
        try:
            docs = self.collection.stream()
            for doc in docs:
                doc.reference.delete()
            return True
        except Exception as e:
            print(f"Erreur lors du nettoyage: {str(e)}")
            return False
