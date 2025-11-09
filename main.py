"""
Application FastAPI principale
Microservice de réponse automatique aux formulaires Google
"""
import os
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

from services.db_factory import get_database_service
from services.smtp_email_service import SMTPEmailService
from services.sms_service import SMSService


# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application FastAPI
app = FastAPI(
    title="Google Forms Auto-Responder",
    description="Microservice d'envoi automatique d'e-mails et SMS lors de soumissions de formulaires Google",
    version="1.0.0"
)

# Configuration CORS pour accepter les requêtes de Google Apps Script
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://script.google.com",
        "https://script.googleusercontent.com",
        "*"  # En production, remplacez par votre domaine spécifique
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser les services
db_service = get_database_service()  # Choisit automatiquement JSON ou Firestore
email_service = None
sms_service = None

# Clé secrète pour authentification webhook
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')


# Modèles Pydantic
class FormResponse(BaseModel):
    """Modèle de réponse du formulaire Google"""
    email: EmailStr
    phone: str
    name: Optional[str] = None
    timestamp: Optional[str] = None
    # Autres champs du formulaire peuvent être ajoutés ici


class StatusResponse(BaseModel):
    """Modèle de réponse pour le statut du service"""
    status: str
    timestamp: str
    services: Dict[str, bool]
    stats: Optional[Dict[str, Any]] = None


# Fonctions utilitaires
def initialize_services():
    """Initialise les services d'envoi (e-mail et SMS)"""
    global email_service, sms_service
    
    try:
        if not email_service:
            email_service = SMTPEmailService()
        if not sms_service:
            sms_service = SMSService()
    except Exception as e:
        print(f"Erreur lors de l'initialisation des services: {str(e)}")


def verify_secret_key(authorization: Optional[str]) -> bool:
    """
    Vérifie la clé secrète dans le header Authorization
    
    Args:
        authorization: Valeur du header Authorization
        
    Returns:
        True si la clé est valide
    """
    if not authorization:
        return False
    
    # Format attendu: "Bearer <secret_key>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            return False
        return token == SECRET_KEY
    except ValueError:
        return False


def generate_response_id(email: str, phone: str, timestamp: Optional[str] = None) -> str:
    """
    Génère un ID unique pour une réponse
    
    Args:
        email: E-mail du répondant
        phone: Téléphone du répondant
        timestamp: Timestamp de la réponse
        
    Returns:
        ID unique hashé
    """
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()
    
    data = f"{email}:{phone}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


# Routes API
@app.get("/")
async def root():
    """Route racine - Information sur l'API"""
    return {
        "service": "Google Forms Auto-Responder",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "status": "/api/status",
            "receive": "/api/receive (POST)"
        }
    }


@app.get("/api/status", response_model=StatusResponse)
async def check_status():
    """
    Endpoint de vérification du statut du service
    Retourne l'état des différents services et statistiques
    """
    initialize_services()
    
    # Vérifier l'état des services
    email_ok = email_service.test_connection() if email_service else False
    sms_ok = sms_service.test_connection() if sms_service else False
    
    # Récupérer les statistiques
    stats = db_service.get_stats()
    
    return StatusResponse(
        status="operational" if email_ok and sms_ok else "degraded",
        timestamp=datetime.utcnow().isoformat() + "Z",
        services={
            "email": email_ok,
            "sms": sms_ok,
            "database": True
        },
        stats=stats
    )


@app.post("/api/receive")
async def receive_form_response(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Endpoint principal pour recevoir les données du formulaire Google
    
    Workflow:
    1. Vérifie l'authentification
    2. Parse les données reçues
    3. Vérifie si déjà traité
    4. Envoie e-mail et SMS
    5. Enregistre dans la base locale
    
    Headers requis:
        Authorization: Bearer <secret_key>
    
    Body (JSON):
        {
            "email": "user@example.com",
            "phone": "+237xxxxxxxx",
            "name": "Nom Prénom",
            "timestamp": "2025-11-08T20:00:00Z"
        }
    """
    # Vérifier l'authentification
    if not verify_secret_key(authorization):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing secret key"
        )
    
    # Initialiser les services si nécessaire
    initialize_services()
    
    try:
        # Parser les données reçues
        data = await request.json()
        
        # Extraire les champs nécessaires
        # Google Apps Script peut envoyer les données sous différents formats
        # On supporte à la fois le format direct et le format namedValues
        if isinstance(data, dict) and 'namedValues' in data:
            # Format Google Apps Script standard
            named_values = data['namedValues']
            email = named_values.get('Adresse e-mail', named_values.get('Email', ['']))[0]
            phone = named_values.get('Téléphone', named_values.get('Phone', ['']))[0]
            name = named_values.get('Nom', named_values.get('Name', ['']))[0]
            timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        else:
            # Format direct
            email = data.get('email')
            phone = data.get('phone')
            name = data.get('name')
            timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        # Valider les données
        if not email or not phone:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: email and phone are mandatory"
            )
        
        # Générer un ID unique pour cette réponse
        response_id = generate_response_id(email, phone, timestamp)
        
        # Vérifier si déjà traité
        if db_service.already_sent(response_id):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "already_processed",
                    "message": "This response has already been processed",
                    "response_id": response_id
                }
            )
        
        # Envoi des messages
        mail_sent = False
        sms_sent = False
        errors = []
        
        # Envoyer l'e-mail
        try:
            if email_service:
                mail_sent = email_service.send_confirmation_email(email, name)
                if not mail_sent:
                    errors.append("Email sending failed")
        except Exception as e:
            errors.append(f"Email error: {str(e)}")
        
        # Envoyer le SMS
        try:
            if sms_service:
                sms_sent = sms_service.send_confirmation_sms(phone, name)
                if not sms_sent:
                    errors.append("SMS sending failed")
        except Exception as e:
            errors.append(f"SMS error: {str(e)}")
        
        # Enregistrer dans la base locale
        db_service.add_response(
            response_id=response_id,
            email=email,
            phone=phone,
            sent_mail=mail_sent,
            sent_sms=sms_sent
        )
        
        # Construire la réponse
        response = {
            "status": "ok" if mail_sent and sms_sent else "partial",
            "response_id": response_id,
            "processed": {
                "email": mail_sent,
                "sms": sms_sent
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if errors:
            response["errors"] = errors
        
        return JSONResponse(
            status_code=200 if mail_sent and sms_sent else 207,
            content=response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/responses")
async def get_all_responses(authorization: Optional[str] = Header(None)):
    """
    Récupère toutes les réponses enregistrées
    (Endpoint d'administration - nécessite authentification)
    """
    if not verify_secret_key(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    responses = db_service.get_all_responses()
    return {
        "total": len(responses),
        "responses": responses
    }


# Événements de démarrage et arrêt
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    print("🚀 Starting Google Forms Auto-Responder...")
    initialize_services()
    print("✅ Services initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt de l'application"""
    print("🛑 Shutting down Google Forms Auto-Responder...")


# Point d'entrée pour exécution directe
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
