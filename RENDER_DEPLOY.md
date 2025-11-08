# 🐳 Guide de déploiement sur Render avec Docker

## 🚀 Déploiement automatique

### 1. Préparer votre repository Git

```powershell
# Initialiser git si pas déjà fait
git init

# Ajouter tous les fichiers
git add .
git commit -m "Initial commit - Auto-responder with Firestore"

# Créer un repository sur GitHub et pousser
git remote add origin https://github.com/votre-username/autoresponder.git
git branch -M main
git push -u origin main
```

### 2. Créer le service sur Render

1. Aller sur [dashboard.render.com](https://dashboard.render.com)
2. Cliquer sur **"New +"** → **"Web Service"**
3. Connecter votre repository GitHub
4. Configurer le service :

   **Paramètres de base :**
   - **Name :** `autoresponder` (ou votre choix)
   - **Region :** Choisir la région la plus proche
   - **Branch :** `main`
   - **Runtime :** `Docker`
   - **Instance Type :** `Free` (ou `Starter` pour production)

   **Build & Deploy :**
   - Render détecte automatiquement le `Dockerfile`
   - Aucune configuration supplémentaire nécessaire

### 3. Configurer les variables d'environnement

Dans l'onglet **"Environment"** de votre service Render, ajouter :

```env
# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application
SMTP_FROM_EMAIL=votre_email@gmail.com

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=votre_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Security
SECRET_KEY=votre_cle_secrete_forte_et_unique

# Firestore Configuration (OBLIGATOIRE)
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"votre-project-id",...}
```

**⚠️ Important pour `FIREBASE_CREDENTIALS_JSON` :**

```powershell
# Ouvrir votre fichier credentials et copier TOUT le contenu
Get-Content firestore-credentials.json -Raw | Set-Clipboard

# Coller dans Render sur UNE SEULE LIGNE (supprimer tous les retours à la ligne)
```

### 4. Déployer

Render va automatiquement :
1. ✅ Détecter le `Dockerfile`
2. ✅ Construire l'image Docker
3. ✅ Démarrer le service
4. ✅ Vous fournir une URL (ex: `https://autoresponder.onrender.com`)

### 5. Mettre à jour Google Apps Script

Une fois déployé, mettre à jour l'URL dans `google-apps-script.js` :

```javascript
const SERVER_URL = 'https://autoresponder.onrender.com';
```

## 🔄 Redéploiement automatique

À chaque `git push`, Render redéploie automatiquement l'application !

```powershell
git add .
git commit -m "Update configuration"
git push origin main
```

## 🧪 Tester le déploiement

```powershell
# Vérifier que le service est en ligne
Invoke-RestMethod -Uri https://votre-service.onrender.com/api/status

# Devrait retourner :
# {
#   "status": "operational",
#   "timestamp": "...",
#   "services": {
#     "email": true,
#     "sms": true,
#     "database": true
#   }
# }
```

## 📊 Avantages de Docker sur Render

✅ **Build reproductible** : même environnement partout  
✅ **Isolation** : toutes les dépendances incluses  
✅ **Déploiement rapide** : cache des layers Docker  
✅ **Scalabilité** : facile à scaler horizontalement  
✅ **Logs centralisés** : accessibles depuis le dashboard Render  

## 🐛 Dépannage

### Le build échoue

```powershell
# Tester localement :
docker build -t autoresponder .
docker run -p 8000:8000 --env-file .env autoresponder
```

### Les variables d'environnement ne sont pas chargées

- Vérifier qu'elles sont bien définies dans Render
- Redéployer le service après modification

### Firestore ne se connecte pas

- Vérifier que `FIREBASE_CREDENTIALS_JSON` est sur UNE seule ligne
- Vérifier que tous les caractères spéciaux sont correctement échappés
- Tester avec le fichier local d'abord

## 💰 Tarification Render

- **Free Tier** : 750h/mois, se met en veille après 15min d'inactivité
- **Starter** : $7/mois, toujours actif, 0.5GB RAM
- **Standard** : $25/mois, 2GB RAM

Pour éviter la mise en veille (plan gratuit), utilisez un service de ping comme [UptimeRobot](https://uptimerobot.com).

## 📚 Ressources

- [Documentation Render Docker](https://render.com/docs/docker)
- [Documentation Render Variables d'environnement](https://render.com/docs/environment-variables)
