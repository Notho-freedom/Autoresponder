# 📘 Google Forms Auto-Responder

Microservice automatique d'envoi d'e-mails et SMS en réponse aux soumissions de formulaires Google.

## 🎯 Fonctionnalités

- ✅ Capture automatique des soumissions Google Forms
- 📧 Envoi automatique d'e-mails de confirmation (SendGrid)
- 📱 Envoi automatique de SMS de confirmation (Twilio)
- 💾 Enregistrement local des réponses traitées (JSON)
- 🔐 Authentification sécurisée par clé secrète
- 📊 API de statut et statistiques
- 🚀 Architecture modulaire et extensible

---

## 🏗️ Architecture

```
[Google Form] 
   ↓ (soumission)
[Apps Script Trigger: onFormSubmit()]
   ↓ (POST JSON avec authentification)
[Serveur FastAPI (Python)]
   ├── Extraction email & téléphone
   ├── Vérification base de données JSON
   ├── Envoi email (SendGrid)
   ├── Envoi SMS (Twilio)
   └── Enregistrement dans responses.json
```

---

## 📦 Structure du projet

```
Autoresponder/
│
├── main.py                  # Application FastAPI principale
├── requirements.txt         # Dépendances Python
├── .env.example            # Template des variables d'environnement
├── google-apps-script.js   # Script pour Google Forms
│
├── services/
│   ├── __init__.py
│   ├── db_service.py       # Gestion base JSON locale
│   ├── email_service.py    # Envoi e-mails via SendGrid
│   └── sms_service.py      # Envoi SMS via Twilio
│
└── data/
    └── responses.json      # Base de données locale
```

---

## 🚀 Installation

### 1. Prérequis

- Python 3.8+
- Compte SendGrid (gratuit : 100 mails/jour)
- Compte Twilio (payant à l'usage)
- Google Form avec un formulaire actif
- **[Pour production]** Compte Firebase avec Firestore activé

### 2. Installation des dépendances

```powershell
# Cloner ou télécharger le projet
cd Autoresponder

# Créer un environnement virtuel (recommandé)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration des variables d'environnement

Copier `.env.example` vers `.env` et remplir les valeurs :

```powershell
Copy-Item .env.example .env
```

Éditer `.env` avec vos vraies valeurs :

```env
# SendGrid Configuration
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@votredomaine.com

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Security
SECRET_KEY=votre_cle_secrete_forte_et_unique

# Database Configuration
# Développement local: false (utilise JSON)
# Production (Render): true (utilise Firestore)
USE_FIRESTORE=false

# Firestore Credentials (uniquement si USE_FIRESTORE=true)
FIREBASE_CREDENTIALS_PATH=firestore-credentials.json
# OU pour production (Render):
# FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

---

## 🔧 Configuration SendGrid

1. Créer un compte sur [sendgrid.com](https://sendgrid.com)
2. Aller dans **Settings** > **API Keys**
3. Créer une nouvelle API Key avec permissions "Mail Send"
4. Copier la clé dans `.env` → `SENDGRID_API_KEY`
5. Configurer l'adresse expéditeur vérifiée dans **Settings** > **Sender Authentication**

**Documentation officielle :** https://docs.sendgrid.com/for-developers/sending-email/api-getting-started

---

## 📱 Configuration Twilio

1. Créer un compte sur [twilio.com](https://www.twilio.com)
2. Obtenir un numéro de téléphone Twilio
3. Noter votre **Account SID** et **Auth Token** (dans le Dashboard)
4. Copier ces valeurs dans `.env`

**Documentation officielle :** https://www.twilio.com/docs/sms/quickstart/python

---

## 🔥 Configuration Firestore (pour production)

### Pourquoi Firestore ?

Sur les plateformes comme **Render**, **Railway**, ou **Fly.io**, le système de fichiers est **éphémère**. À chaque redéploiement ou mise à jour, tous les fichiers (y compris `responses.json`) sont **supprimés**.

**Solution :** Utiliser **Firestore** (base de données NoSQL de Firebase) pour un stockage persistant.

### 1. Créer un projet Firebase

1. Aller sur [console.firebase.google.com](https://console.firebase.google.com)
2. Créer un nouveau projet (ou utiliser un existant)
3. Cliquer sur **"Créer une base de données"** dans Firestore Database
4. Choisir le mode **"Production"** ou **"Test"**
5. Sélectionner une région proche de vos utilisateurs

### 2. Créer un compte de service

1. Dans la console Firebase, aller dans **⚙️ Paramètres du projet**
2. Onglet **"Comptes de service"**
3. Cliquer sur **"Générer une nouvelle clé privée"**
4. Un fichier JSON sera téléchargé (ex: `mon-projet-firebase-adminsdk-xxxxx.json`)

### 3. Configuration locale (développement)

```powershell
# Renommer le fichier téléchargé
Rename-Item mon-projet-firebase-adminsdk-xxxxx.json firestore-credentials.json

# Activer Firestore dans .env
# Éditer .env et mettre:
USE_FIRESTORE=true
FIREBASE_CREDENTIALS_PATH=firestore-credentials.json
```

### 4. Configuration Render (production)

Sur Render, il faut passer les credentials en **variable d'environnement** (pas de fichier) :

```powershell
# Ouvrir le fichier JSON et copier TOUT son contenu
Get-Content firestore-credentials.json -Raw

# Aller sur le dashboard Render
# Environment > Add Environment Variable
# Nom: FIREBASE_CREDENTIALS_JSON
# Valeur: [coller tout le JSON sur une seule ligne]
# Exemple: {"type":"service_account","project_id":"mon-projet","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n..."}

# Ajouter aussi:
# USE_FIRESTORE=true
```

### 5. Règles de sécurité Firestore

Dans la console Firebase > Firestore Database > Règles, utiliser :

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Autoriser uniquement l'authentification serveur
    match /responses/{document=**} {
      allow read, write: if false;  // Personne ne peut accéder directement
    }
  }
}
```

Les accès se font uniquement via le SDK Admin (votre backend), pas depuis les clients.

**Documentation Firestore :** https://firebase.google.com/docs/firestore

---

## 🌐 Déploiement du serveur

### Option A : Local (développement)

```powershell
# Lancer le serveur
python main.py

# Ou avec uvicorn directement
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur `http://localhost:8000`

### Option B : Déploiement en production

**Plateformes recommandées (gratuites) :**

#### Render.com
1. Créer un compte sur [render.com](https://render.com)
2. Nouveau Web Service → Connecter votre repository Git
3. Build Command : `pip install -r requirements.txt`
4. Start Command : `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Ajouter les variables d'environnement :
   ```
   SENDGRID_API_KEY=SG.xxx...
   TWILIO_ACCOUNT_SID=ACxxx...
   TWILIO_AUTH_TOKEN=xxx...
   TWILIO_PHONE_NUMBER=+1234567890
   SENDGRID_FROM_EMAIL=noreply@votredomaine.com
   SECRET_KEY=votre_cle_secrete
   USE_FIRESTORE=true
   FIREBASE_CREDENTIALS_JSON={"type":"service_account"...}
   ```
6. Déployer !

**⚠️ IMPORTANT pour Render :** Vous **devez** utiliser Firestore (voir section Configuration Firestore ci-dessous)

#### Railway.app
1. Créer un compte sur [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Ajouter les variables d'environnement (incluant Firestore si production)
4. Le déploiement est automatique

**💡 Astuce :** Railway aussi a un système de fichiers éphémère, donc utilisez Firestore

#### Fly.io
```powershell
# Installer flyctl
# Voir : https://fly.io/docs/hands-on/install-flyctl/

# Se connecter
fly auth login

# Lancer l'application
fly launch

# Configurer les variables d'environnement
fly secrets set SENDGRID_API_KEY=xxx TWILIO_ACCOUNT_SID=xxx ...
```

---

## 🔗 Configuration Google Apps Script

### 1. Ouvrir l'éditeur de scripts

1. Ouvrir votre Google Form
2. Cliquer sur les **trois points ⋮** en haut à droite
3. Sélectionner **"Éditeur de scripts"**

### 2. Coller le script

1. Copier tout le contenu de `google-apps-script.js`
2. Coller dans l'éditeur Google Apps Script
3. **Modifier les constantes de configuration :**

```javascript
const SERVER_URL = 'https://votre-serveur-render.com';  // VOTRE URL
const SECRET_KEY = 'votre_cle_secrete';                 // LA MÊME QUE DANS .env
const EMAIL_FIELD_NAME = 'Adresse e-mail';              // Nom exact du champ email
const PHONE_FIELD_NAME = 'Téléphone';                   // Nom exact du champ téléphone
const NAME_FIELD_NAME = 'Nom';                          // Nom exact du champ nom
```

💡 **Astuce :** Exécuter la fonction `listFormFields()` dans l'éditeur pour voir les noms exacts de vos champs.

### 3. Créer le déclencheur

1. Cliquer sur l'icône **horloge ⏰** (Déclencheurs)
2. Cliquer sur **"+ Ajouter un déclencheur"**
3. Configurer :
   - **Fonction à exécuter :** `onFormSubmit`
   - **Source de l'événement :** `Depuis le formulaire`
   - **Type d'événement :** `Lors de l'envoi du formulaire`
4. Cliquer sur **"Enregistrer"**
5. Autoriser les permissions si demandé

### 4. Tester

- Exécuter `testServerConnection()` pour vérifier la connexion
- Exécuter `testManual()` pour simuler une soumission
- Soumettre le formulaire pour tester en conditions réelles

---

## 📡 Endpoints API

### `GET /`
Informations sur l'API

**Réponse :**
```json
{
  "service": "Google Forms Auto-Responder",
  "version": "1.0.0",
  "status": "running"
}
```

---

### `GET /api/status`
Statut du service et statistiques

**Réponse :**
```json
{
  "status": "operational",
  "timestamp": "2025-11-08T20:00:00Z",
  "services": {
    "email": true,
    "sms": true,
    "database": true
  },
  "stats": {
    "total_responses": 42,
    "mails_sent": 42,
    "sms_sent": 40,
    "success_rate": 97.62
  }
}
```

---

### `POST /api/receive`
Reçoit les données du formulaire (appelé par Google Apps Script)

**Headers :**
```
Authorization: Bearer YOUR_SECRET_KEY
Content-Type: application/json
```

**Body :**
```json
{
  "email": "user@example.com",
  "phone": "+237600000000",
  "name": "Jean Dupont",
  "timestamp": "2025-11-08T20:00:00Z"
}
```

**Réponse succès (200) :**
```json
{
  "status": "ok",
  "response_id": "abc123def456",
  "processed": {
    "email": true,
    "sms": true
  },
  "timestamp": "2025-11-08T20:00:00Z"
}
```

**Réponse partielle (207) :**
```json
{
  "status": "partial",
  "response_id": "abc123def456",
  "processed": {
    "email": true,
    "sms": false
  },
  "errors": ["SMS sending failed"],
  "timestamp": "2025-11-08T20:00:00Z"
}
```

---

### `GET /api/responses`
Liste toutes les réponses enregistrées (admin)

**Headers :**
```
Authorization: Bearer YOUR_SECRET_KEY
```

**Réponse :**
```json
{
  "total": 2,
  "responses": [
    {
      "responseId": "abc123",
      "email": "test@example.com",
      "phone": "+237600000000",
      "sent_mail": true,
      "sent_sms": true,
      "timestamp": "2025-11-08T20:00:00Z"
    }
  ]
}
```

---

## 🧪 Tests

### Tester le serveur local

```powershell
# Lancer le serveur
python main.py

# Dans un autre terminal, tester l'API
Invoke-RestMethod -Uri http://localhost:8000/api/status -Method Get

# Tester l'endpoint receive
$headers = @{
    "Authorization" = "Bearer your_secret_key_here"
    "Content-Type" = "application/json"
}

$body = @{
    email = "test@example.com"
    phone = "+237600000000"
    name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/api/receive -Method Post -Headers $headers -Body $body
```

### Tester Google Apps Script

1. Dans l'éditeur Apps Script, exécuter `testManual()`
2. Vérifier les logs (Affichage > Journaux)
3. Soumettre le formulaire réellement

---

## 🔐 Sécurité

### Bonnes pratiques

1. **Ne jamais commiter le fichier `.env`** (déjà dans `.gitignore`)
2. **Utiliser une clé secrète forte** : générer avec `openssl rand -hex 32`
3. **Activer HTTPS** en production (automatique sur Render, Railway, Fly.io)
4. **Restreindre les permissions** SendGrid et Twilio au minimum nécessaire
5. **Monitorer les logs** pour détecter les abus

### Générer une clé secrète forte

```powershell
# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

---

## 💰 Tarification

| Service | Plan gratuit | Tarif payant |
|---------|--------------|--------------|
| **SendGrid** | 100 mails/jour gratuits | À partir de $14.95/mois |
| **Twilio SMS** | Crédit d'essai (~$15) | ~0,05€ par SMS |
| **Firebase Firestore** | 50k lectures + 20k écritures/jour gratuites | Pay-as-you-go au-delà |
| **Render.com** | 750h/mois gratuit | À partir de $7/mois |
| **Railway.app** | $5 crédit gratuit/mois | Pay-as-you-go |

---

## 📈 Évolutions futures

- [x] Support Firestore pour déploiement cloud
- [ ] Migration automatique JSON → Firestore
- [ ] Tableau de bord web pour monitoring
- [ ] Support WhatsApp via Twilio API
- [ ] Templates personnalisables (mail + SMS)
- [ ] Envoi différé / planifié
- [ ] Support multi-formulaires
- [ ] Webhooks pour intégrations tierces
- [ ] Authentification JWT avancée
- [ ] Backup automatique Firestore

---

## 🐛 Dépannage

### Le serveur ne démarre pas

```powershell
# Vérifier les dépendances
pip install -r requirements.txt --upgrade

# Vérifier les variables d'environnement
Get-Content .env
```

### Les e-mails ne partent pas

- Vérifier la clé API SendGrid
- Vérifier que l'adresse expéditeur est vérifiée
- Consulter les logs SendGrid : [sendgrid.com/email_activity](https://app.sendgrid.com/email_activity)

### Les SMS ne partent pas

- Vérifier les crédits Twilio
- Vérifier le format du numéro (international: +237...)
- Consulter les logs Twilio : [console.twilio.com](https://console.twilio.com)

### Google Apps Script ne se déclenche pas

- Vérifier que le déclencheur est bien créé
- Vérifier les logs : Exécutions > Journal
- Tester manuellement avec `testManual()`

### Erreur 401 Unauthorized

- Vérifier que `SECRET_KEY` est identique dans `.env` et `google-apps-script.js`
- Vérifier le format du header : `Authorization: Bearer YOUR_KEY`

### Problèmes avec Firestore

- Vérifier que le projet Firebase existe
- Vérifier que Firestore est activé dans la console
- Vérifier les credentials JSON (format valide)
- Consulter les logs Firestore dans la console Firebase
- Sur Render : vérifier que `FIREBASE_CREDENTIALS_JSON` contient tout le JSON sur une ligne

### Migration JSON → Firestore

Si vous avez déjà des données dans `responses.json` :

```python
# Script de migration simple (à exécuter localement)
import json
from services.firestore_service import FirestoreService

# Charger les données JSON
with open('data/responses.json', 'r') as f:
    data = json.load(f)

# Initialiser Firestore
fs = FirestoreService(credentials_path='firestore-credentials.json')

# Migrer chaque réponse
for response in data:
    fs.add_response(
        response_id=response['responseId'],
        email=response['email'],
        phone=response['phone'],
        sent_mail=response.get('sent_mail', True),
        sent_sms=response.get('sent_sms', True)
    )

print(f"✅ {len(data)} réponses migrées vers Firestore")
```

---

## 📚 Documentation des APIs

- **FastAPI :** https://fastapi.tiangolo.com
- **SendGrid :** https://docs.sendgrid.com
- **Twilio :** https://www.twilio.com/docs
- **Google Apps Script :** https://developers.google.com/apps-script

---

## 📝 Licence

Ce projet est fourni à titre d'exemple et peut être utilisé librement.

---

## 🤝 Support

Pour toute question ou problème :
1. Vérifier la section **Dépannage** ci-dessus
2. Consulter les logs du serveur et de Google Apps Script
3. Vérifier la documentation des APIs externes

---

## ✅ Checklist de déploiement

### Développement local
- [ ] Installer Python et dépendances
- [ ] Créer compte SendGrid et obtenir API key
- [ ] Créer compte Twilio et obtenir credentials
- [ ] Configurer le fichier `.env` (avec `USE_FIRESTORE=false`)
- [ ] Tester le serveur en local
- [ ] Configurer Google Apps Script avec `http://localhost:8000`
- [ ] Tester avec une soumission de formulaire

### Production (Render/Railway)
- [ ] Créer projet Firebase et activer Firestore
- [ ] Générer les credentials de compte de service Firebase
- [ ] Déployer sur plateforme cloud (Render/Railway/Fly.io)
- [ ] Configurer les variables d'environnement (avec `USE_FIRESTORE=true`)
- [ ] Ajouter `FIREBASE_CREDENTIALS_JSON` avec le JSON complet
- [ ] Mettre à jour Google Apps Script avec l'URL de production
- [ ] Créer le déclencheur dans Google Apps Script
- [ ] Tester avec une vraie soumission de formulaire
- [ ] Vérifier la réception des e-mails et SMS
- [ ] Vérifier les données dans Firestore Console
- [ ] Monitorer les logs pour les premières heures

---

**🎉 Votre système d'auto-réponse est prêt !**
