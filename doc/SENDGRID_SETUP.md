# Configuration SendGrid pour Render

## 📧 **Étapes pour obtenir votre API Key SendGrid:**

### 1. **Créer un compte SendGrid** (gratuit)
   - Allez sur https://signup.sendgrid.com/
   - Inscrivez-vous avec votre email
   - Vérifiez votre email

### 2. **Créer une API Key**
   - Connectez-vous à https://app.sendgrid.com/
   - Allez dans **Settings** > **API Keys**
   - Cliquez sur **Create API Key**
   - Nom: `Autoresponder-Render`
   - Permissions: **Full Access** (ou au minimum **Mail Send**)
   - Cliquez **Create & View**
   - **COPIEZ LA CLÉ** (elle ne sera affichée qu'une seule fois!)

### 3. **Vérifier votre domaine d'envoi**
   - Allez dans **Settings** > **Sender Authentication**
   - Cliquez sur **Verify a Single Sender**
   - Remplissez avec `oragroup24@gmail.com`
   - Vérifiez votre email Gmail et cliquez sur le lien

### 4. **Configurer sur Render**
   - Allez sur https://dashboard.render.com
   - Sélectionnez votre service `autoresponder-qkpe`
   - Onglet **Environment**
   - Ajoutez/Modifiez ces variables:
   
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SENDGRID_FROM_EMAIL=oragroup24@gmail.com
   ```

### 5. **Redéployer**
   - Dans l'onglet **Manual Deploy**, cliquez **Clear build cache & deploy**
   - Attendez que le déploiement soit terminé (~5 minutes)

### 6. **Tester**
   - Soumettez un formulaire Google
   - Vérifiez l'email!

## 📊 **Limites SendGrid (gratuit):**
- 100 emails/jour
- Parfait pour les tests et petits projets
- Pas besoin de carte bancaire

## 🔧 **Installation locale (optionnel):**

Si vous voulez tester en local avec SendGrid:

```bash
pip install sendgrid
```

Puis dans votre `.env` local, ajoutez votre `SENDGRID_API_KEY`.

---

**Note:** SendGrid fonctionne partout (Render, Railway, Heroku, etc.) car il utilise une API HTTP au lieu de SMTP qui est souvent bloqué.
