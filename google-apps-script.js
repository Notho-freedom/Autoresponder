/**
 * Google Apps Script - Déclencheur automatique pour Google Forms
 * 
 * INSTALLATION:
 * 1. Ouvrir votre Google Form
 * 2. Cliquer sur les trois points ⋮ en haut à droite
 * 3. Sélectionner "Éditeur de scripts"
 * 4. Coller ce code dans l'éditeur
 * 5. Remplacer YOUR_SERVER_URL et YOUR_SECRET_KEY par vos valeurs
 * 6. Sauvegarder le script
 * 7. Créer un déclencheur :
 *    - Cliquer sur l'horloge ⏰ (Déclencheurs)
 *    - "+ Ajouter un déclencheur"
 *    - Fonction : onFormSubmit
 *    - Source de l'événement : Depuis le formulaire
 *    - Type d'événement : Lors de l'envoi du formulaire
 *    - Enregistrer
 */

// ==================== CONFIGURATION ====================
// ⚠️ IMPORTANT : Remplacez ces valeurs par les vôtres

// URL de votre serveur backend (sans slash final)
const SERVER_URL = 'https://votre-serveur.com';

// Clé secrète pour authentifier les requêtes (doit correspondre à celle du backend)
const SECRET_KEY = 'your_secret_key_for_webhook_authentication';

// Nom des champs du formulaire (à adapter selon votre formulaire)
const EMAIL_FIELD_NAME = 'Adresse e-mail';  // ou 'Email' selon votre formulaire
const PHONE_FIELD_NAME = 'Téléphone';       // ou 'Phone' selon votre formulaire
const NAME_FIELD_NAME = 'Nom';              // ou 'Name' (optionnel)

// =======================================================


/**
 * Fonction déclenchée automatiquement lors de la soumission du formulaire
 * @param {Object} e - Objet événement contenant les données du formulaire
 */
function onFormSubmit(e) {
  try {
    // Log de l'objet e pour debugging
    Logger.log('📝 Nouvelle soumission de formulaire reçue');
    Logger.log('Type de e: ' + typeof e);
    Logger.log('Contenu de e: ' + JSON.stringify(e));
    
    // Récupérer les réponses du formulaire
    // Méthode alternative si e.namedValues est undefined
    let namedValues;
    
    if (e && e.namedValues) {
      // Méthode standard avec déclencheur
      namedValues = e.namedValues;
      Logger.log('✅ Utilisation de e.namedValues');
    } else if (e && e.response) {
      // Méthode alternative avec e.response
      namedValues = e.response.getItemResponses().reduce((acc, item) => {
        const title = item.getItem().getTitle();
        const response = item.getResponse();
        acc[title] = Array.isArray(response) ? response : [response];
        return acc;
      }, {});
      Logger.log('✅ Utilisation de e.response (méthode alternative)');
    } else {
      // Dernière tentative : récupérer directement du formulaire
      const form = FormApp.getActiveForm();
      const formResponses = form.getResponses();
      if (formResponses.length > 0) {
        const lastResponse = formResponses[formResponses.length - 1];
        namedValues = lastResponse.getItemResponses().reduce((acc, item) => {
          const title = item.getItem().getTitle();
          const response = item.getResponse();
          acc[title] = Array.isArray(response) ? response : [response];
          return acc;
        }, {});
        Logger.log('✅ Récupération de la dernière réponse du formulaire');
      } else {
        Logger.log('❌ Aucune donnée disponible');
        return;
      }
    }
    
    Logger.log('Données extraites: ' + JSON.stringify(namedValues));
    
    // Extraire les champs nécessaires (toujours extraire la première valeur du tableau)
    let email = getFieldValue(namedValues, EMAIL_FIELD_NAME);
    let phone = getFieldValue(namedValues, PHONE_FIELD_NAME);
    let name = getFieldValue(namedValues, NAME_FIELD_NAME);
    
    // Si les valeurs sont toujours des tableaux, extraire le premier élément
    if (Array.isArray(email)) email = email[0] || '';
    if (Array.isArray(phone)) phone = phone[0] || '';
    if (Array.isArray(name)) name = name[0] || '';
    
    // Vérifier que les champs obligatoires sont présents
    if (!email || !phone) {
      Logger.log('❌ Erreur : e-mail ou téléphone manquant');
      Logger.log('Email: ' + email);
      Logger.log('Phone: ' + phone);
      Logger.log('Champs disponibles: ' + Object.keys(namedValues).join(', '));
      return;
    }
    
    // Construire le payload à envoyer (avec chaînes simples, pas de tableaux)
    const payload = {
      email: String(email),
      phone: String(phone),
      name: String(name || ''),
      timestamp: new Date().toISOString()
    };
    
    // Options de la requête HTTP
    const options = {
      method: 'post',
      contentType: 'application/json',
      headers: {
        'Authorization': 'Bearer ' + SECRET_KEY
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true  // Pour gérer les erreurs HTTP manuellement
    };
    
    // Envoyer la requête au backend
    Logger.log('📤 Envoi des données au backend...');
    const response = UrlFetchApp.fetch(SERVER_URL + '/api/receive', options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    // Log de la réponse
    if (responseCode >= 200 && responseCode < 300) {
      Logger.log('✅ Succès ! Réponse du serveur : ' + responseText);
    } else {
      Logger.log('⚠️ Erreur HTTP ' + responseCode + ' : ' + responseText);
    }
    
  } catch (error) {
    // Gestion des erreurs
    Logger.log('❌ Erreur lors du traitement : ' + error.toString());
    
    // Optionnel : Envoyer une notification par e-mail en cas d'erreur
    // MailApp.sendEmail('admin@example.com', 'Erreur Auto-Responder', error.toString());
  }
}


/**
 * Fonction utilitaire pour extraire une valeur d'un champ
 * @param {Object} namedValues - Objet contenant toutes les réponses
 * @param {string} fieldName - Nom du champ à extraire
 * @return {string} La valeur du champ ou chaîne vide
 */
function getFieldValue(namedValues, fieldName) {
  if (!fieldName) return '';
  
  // Chercher le champ (insensible à la casse)
  for (const key in namedValues) {
    if (key.toLowerCase() === fieldName.toLowerCase()) {
      const value = namedValues[key];
      // Retourner la première valeur si c'est un tableau
      return Array.isArray(value) ? value[0] : value;
    }
  }
  
  return '';
}


/**
 * Fonction de test manuelle (utile pour débugger)
 * Pour tester : Exécution > Exécuter la fonction > testManual
 */
function testManual() {
  // Simuler un événement de soumission
  const mockEvent = {
    namedValues: {
      'Adresse e-mail': ['test@example.com'],
      'Téléphone': ['+237600000000'],
      'Nom': ['Test Utilisateur']
    }
  };
  
  Logger.log('🧪 Test manuel du script...');
  onFormSubmit(mockEvent);
}


/**
 * Fonction pour afficher tous les noms de champs du formulaire
 * Utile pour identifier les noms exacts des champs
 * Pour utiliser : Exécution > Exécuter la fonction > listFormFields
 */
function listFormFields() {
  const form = FormApp.getActiveForm();
  const items = form.getItems();
  
  Logger.log('📋 Liste des champs du formulaire :');
  Logger.log('================================');
  
  items.forEach(function(item) {
    const title = item.getTitle();
    const type = item.getType();
    Logger.log('- Champ : "' + title + '" | Type : ' + type);
  });
  
  Logger.log('================================');
  Logger.log('💡 Utilisez ces noms exacts dans la configuration ci-dessus');
}


/**
 * Fonction pour tester la connexion au serveur backend
 * Pour utiliser : Exécution > Exécuter la fonction > testServerConnection
 */
function testServerConnection() {
  try {
    Logger.log('🔌 Test de connexion au serveur...');
    
    const options = {
      method: 'get',
      muteHttpExceptions: true
    };
    
    const response = UrlFetchApp.fetch(SERVER_URL + '/api/status', options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    if (responseCode === 200) {
      Logger.log('✅ Connexion réussie !');
      Logger.log('Réponse : ' + responseText);
    } else {
      Logger.log('⚠️ Serveur accessible mais code HTTP : ' + responseCode);
      Logger.log('Réponse : ' + responseText);
    }
    
  } catch (error) {
    Logger.log('❌ Impossible de se connecter au serveur');
    Logger.log('Erreur : ' + error.toString());
    Logger.log('Vérifiez que SERVER_URL est correct et que le serveur est en ligne');
  }
}
