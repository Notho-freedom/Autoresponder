"""
Service de gestion de la base de données locale JSON
Gère l'enregistrement et la vérification des réponses déjà traitées
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict


class DatabaseService:
    def __init__(self, db_path: str = "data/responses.json"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Crée le fichier JSON s'il n'existe pas"""
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _read_db(self) -> List[Dict]:
        """Lit le contenu de la base de données"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_db(self, data: List[Dict]):
        """Écrit dans la base de données"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def already_sent(self, response_id: str) -> bool:
        """
        Vérifie si une réponse a déjà été traitée
        
        Args:
            response_id: Identifiant unique de la réponse
            
        Returns:
            True si déjà envoyé, False sinon
        """
        data = self._read_db()
        return any(entry.get('responseId') == response_id for entry in data)
    
    def add_response(self, response_id: str, email: str, phone: str, 
                    sent_mail: bool = True, sent_sms: bool = True) -> bool:
        """
        Ajoute une nouvelle réponse traitée dans la base
        
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
        
        data = self._read_db()
        new_entry = {
            "responseId": response_id,
            "email": email,
            "phone": phone,
            "sent_mail": sent_mail,
            "sent_sms": sent_sms,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        data.append(new_entry)
        self._write_db(data)
        return True
    
    def get_response(self, response_id: str) -> Optional[Dict]:
        """
        Récupère une réponse spécifique par son ID
        
        Args:
            response_id: Identifiant unique de la réponse
            
        Returns:
            Les données de la réponse ou None si non trouvée
        """
        data = self._read_db()
        for entry in data:
            if entry.get('responseId') == response_id:
                return entry
        return None
    
    def get_all_responses(self) -> List[Dict]:
        """Récupère toutes les réponses enregistrées"""
        return self._read_db()
    
    def get_stats(self) -> Dict:
        """
        Génère des statistiques sur les envois
        
        Returns:
            Dictionnaire avec les statistiques
        """
        data = self._read_db()
        total = len(data)
        mails_sent = sum(1 for entry in data if entry.get('sent_mail', False))
        sms_sent = sum(1 for entry in data if entry.get('sent_sms', False))
        
        return {
            "total_responses": total,
            "mails_sent": mails_sent,
            "sms_sent": sms_sent,
            "success_rate": 100 if total == 0 else round((mails_sent + sms_sent) / (total * 2) * 100, 2)
        }
