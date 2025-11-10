# 📦 Guide des Providers Multi-Services

Le système supporte maintenant **plusieurs providers** pour les emails et SMS, activables via variables d'environnement.

## 🎯 Configuration

### Variables d'Environnement Principales

```env
# ============= PROVIDER SELECTION =============
# Email Provider: sendgrid or smtp
EMAIL_PROVIDER=sendgrid

# SMS Provider: twilio or sns
SMS_PROVIDER=twilio
```

---

## 📧 **EMAIL PROVIDERS**

### 1. SendGrid (Recommandé pour production)

**Avantages:**
- ✅ API RESTful rapide et fiable
- ✅ Délivrabilité optimale (SPF/DKIM)
- ✅ Authentification domaine facile
- ✅ 100 emails/jour gratuits
- ✅ Dashboard avec stats détaillées

**Configuration `.env`:**
```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=no-reply@yourdomain.com
SENDGRID_REPLY_TO_EMAIL=support@yourdomain.com
SENDGRID_EMAIL_NAME=Your Company Name
```

**Setup SendGrid:**
1. Créer compte sur [SendGrid](https://sendgrid.com/)
2. Aller dans Settings → API Keys → Create API Key
3. Choisir "Full Access" ou "Mail Send" uniquement
4. **Important:** Authentifier votre domaine (Settings → Sender Authentication → Domain Authentication)

---

### 2. SMTP/Gmail (Local ou petit volume)

**Avantages:**
- ✅ Gratuit avec Gmail
- ✅ Aucune inscription tierce
- ✅ Compatible avec tout serveur SMTP (Outlook, ProtonMail, etc.)
- ✅ Idéal pour tests locaux

**Limitations:**
- ⚠️ Gmail: 500 emails/jour max
- ⚠️ Risque spam si domaine non authentifié
- ⚠️ Plus lent qu'une API

**Configuration `.env`:**
```env
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=Your Company Name
```

**Setup Gmail:**
1. Activer "Validation en 2 étapes" sur votre compte Google
2. Aller dans Compte Google → Sécurité → Mots de passe des applications
3. Générer un mot de passe d'application (sélectionner "Autre")
4. Utiliser ce mot de passe dans `SMTP_PASSWORD`

---

## 📱 **SMS PROVIDERS**

### 1. Twilio (Recommandé)

**Avantages:**
- ✅ Le plus populaire et fiable
- ✅ Coverage mondiale (220+ pays)
- ✅ API simple et bien documentée
- ✅ Crédit gratuit $15-20 à l'inscription
- ✅ Numéros locaux disponibles

**Tarifs:** ~$0.0075/SMS (varie selon pays)

**Configuration `.env`:**
```env
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

**Setup Twilio:**
1. Créer compte sur [Twilio](https://www.twilio.com/)
2. Aller dans Console → Account Info
3. Copier Account SID et Auth Token
4. Acheter un numéro de téléphone (Phone Numbers → Buy a Number)
5. Vérifier les numéros destinataires en mode trial

---

### 2. AWS SNS (Alternative scalable)

**Avantages:**
- ✅ Intégré dans écosystème AWS
- ✅ Très scalable (millions de SMS)
- ✅ Prix compétitifs (~$0.00645/SMS)
- ✅ Pas besoin d'acheter un numéro
- ✅ Free tier: 100 SMS/mois gratuits

**Limitations:**
- ⚠️ Configuration IAM plus complexe
- ⚠️ Moins de features que Twilio
- ⚠️ SenderID limité à 11 caractères

**Configuration `.env`:**
```env
SMS_PROVIDER=sns
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
AWS_SNS_SENDER_ID=YourApp
```

**Setup AWS SNS:**
1. Créer compte AWS
2. Aller dans IAM → Users → Create User
3. Donner permissions: `SNSFullAccess` ou `SNSPublish`
4. Créer Access Key (Security Credentials)
5. Configurer quota SMS dans SNS console (Default spending limit: $1/mois)
6. Vérifier pays supportés: [AWS SNS Coverage](https://docs.aws.amazon.com/sns/latest/dg/sns-supported-regions-countries.html)

---

## 🔄 **Changer de Provider**

### Passer de SendGrid à SMTP:
```env
EMAIL_PROVIDER=smtp
# Ajouter credentials SMTP
```

### Passer de Twilio à AWS SNS:
```env
SMS_PROVIDER=sns
# Ajouter credentials AWS
```

**Redémarrer le serveur** après changement!

---

## 🧪 **Tests Locaux**

### Test Email SendGrid:
```python
from services.sendgrid_email_service import SendGridEmailService
service = SendGridEmailService()
result = service.send_confirmation_email("test@example.com", "John")
print(f"Email sent: {result}")
```

### Test Email SMTP:
```python
from services.smtp_email_service import SMTPEmailService
service = SMTPEmailService()
result = service.send_confirmation_email("test@example.com", "John")
print(f"Email sent: {result}")
```

### Test SMS Twilio:
```python
from services.sms_service import SMSService
service = SMSService()
result = service.send_confirmation_sms("+1234567890", "John")
print(f"SMS sent: {result}")
```

### Test SMS AWS SNS:
```python
from services.aws_sns_service import AWSSNSService
service = AWSSNSService()
result = service.send_confirmation_sms("+1234567890", "John")
print(f"SMS sent: {result}")
```

---

## 📊 **Comparaison des Providers**

### Emails

| Feature | SendGrid | SMTP/Gmail |
|---------|----------|------------|
| **Vitesse** | ⚡ Très rapide (API) | 🐢 Lent (protocole SMTP) |
| **Délivrabilité** | ✅ Excellente (SPF/DKIM) | ⚠️ Moyenne |
| **Gratuit** | 100/jour | 500/jour (Gmail) |
| **Setup** | API Key simple | Mot de passe app |
| **Production** | ✅ Recommandé | ❌ Déconseillé |
| **Local/Test** | ✅ OK | ✅ Parfait |

### SMS

| Feature | Twilio | AWS SNS |
|---------|--------|---------|
| **Facilité** | ✅ Très simple | ⚠️ Configuration AWS |
| **Coverage** | 🌍 220+ pays | 🌍 200+ pays |
| **Prix** | $0.0075/SMS | $0.00645/SMS |
| **Gratuit** | $15-20 crédit | 100 SMS/mois |
| **Features** | ✅✅ Nombreuses | ⚠️ Basiques |
| **Production** | ✅ Recommandé | ✅ OK si déjà AWS |

---

## ⚙️ **Recommandations**

### 🏠 **Développement Local:**
```env
EMAIL_PROVIDER=smtp      # Gmail gratuit
SMS_PROVIDER=twilio      # Crédit gratuit
```

### 🚀 **Production (Startup):**
```env
EMAIL_PROVIDER=sendgrid  # Délivrabilité optimale
SMS_PROVIDER=twilio      # Plus simple et fiable
```

### 🏢 **Production (AWS Infrastructure):**
```env
EMAIL_PROVIDER=sendgrid  # Toujours SendGrid
SMS_PROVIDER=sns         # Intégré AWS, moins cher
```

---

## 🔍 **Logs et Monitoring**

Tous les providers loguent leurs actions:

```
2025-11-10 15:02:20 - utils.service_manager - INFO - Email service initialized: SendGrid
2025-11-10 15:02:21 - services.sendgrid_email_service - INFO - Email sent successfully to user@example.com via SendGrid
2025-11-10 15:02:22 - services.sms_service - INFO - SMS sent successfully to +1234567890
```

Vérifier les logs pour diagnostiquer les problèmes!

---

## 🆘 **Troubleshooting**

### Email non reçu (SendGrid):
1. ✅ Vérifier spam/indésirables
2. ✅ Authentifier le domaine (SPF/DKIM)
3. ✅ Vérifier Dashboard SendGrid → Activity

### Email non reçu (SMTP):
1. ✅ Vérifier mot de passe application
2. ✅ Activer "Validation en 2 étapes" (Gmail)
3. ✅ Vérifier firewall/antivirus

### SMS non reçu (Twilio):
1. ✅ Mode trial: vérifier numéro destinataire
2. ✅ Vérifier crédit restant
3. ✅ Vérifier Twilio Console → Logs

### SMS non reçu (AWS SNS):
1. ✅ Vérifier quota SMS (Default: $1/mois)
2. ✅ Vérifier pays supporté
3. ✅ Vérifier IAM permissions
4. ✅ CloudWatch Logs → SNS

---

## 📚 **Documentation Officielle**

- [SendGrid API Docs](https://docs.sendgrid.com/)
- [Twilio SMS Docs](https://www.twilio.com/docs/sms)
- [AWS SNS Docs](https://docs.aws.amazon.com/sns/latest/dg/sns-sms.html)
- [Gmail SMTP Guide](https://support.google.com/a/answer/176600)
