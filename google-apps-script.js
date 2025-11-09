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
    Logger.log('📝 Nouvelle soumission de formulaire reçue');
    
    // Récupérer les données avec stratégie de fallback robuste
    const namedValues = extractFormData(e);
    
    if (!namedValues || Object.keys(namedValues).length === 0) {
      Logger.log('❌ Impossible d\'extraire les données du formulaire');
      return;
    }
    
    Logger.log('✅ Données extraites: ' + JSON.stringify(namedValues));
    Logger.log('📋 Champs disponibles: ' + Object.keys(namedValues).join(', '));
    
    // Extraction intelligente des champs avec multiples tentatives
    const email = extractField(namedValues, [
      EMAIL_FIELD_NAME,
      'email',
      'e-mail',
      'Email',
      'E-mail',
      'Adresse e-mail',
      'Adresse électronique',
      'Mail'
    ]);
    
    const phone = extractField(namedValues, [
      PHONE_FIELD_NAME,
      'phone',
      'téléphone',
      'telephone',
      'Phone',
      'Téléphone',
      'Numéro de téléphone',
      'Numéro',
      'Tel',
      'Tél'
    ]);
    
    const name = extractField(namedValues, [
      NAME_FIELD_NAME,
      'name',
      'nom',
      'Name',
      'Nom',
      'Nom complet',
      'Prénom',
      'prenom',
      'Nom et prénom'
    ]);
    
    // Validation stricte des champs obligatoires
    if (!email || !isValidEmail(email)) {
      Logger.log('❌ Email manquant ou invalide: ' + email);
      Logger.log('💡 Vérifiez que le champ email existe: ' + Object.keys(namedValues).join(', '));
      return;
    }
    
    if (!phone || !isValidPhone(phone)) {
      Logger.log('❌ Téléphone manquant ou invalide: ' + phone);
      Logger.log('💡 Vérifiez que le champ téléphone existe: ' + Object.keys(namedValues).join(', '));
      return;
    }
    
    Logger.log('✅ Email validé: ' + email);
    Logger.log('✅ Téléphone validé: ' + phone);
    Logger.log('ℹ️  Nom: ' + (name || '(non fourni)'));
    
    // Construire le payload nettoyé
    const payload = {
      email: cleanString(email),
      phone: cleanString(phone),
      name: cleanString(name || ''),
      timestamp: new Date().toISOString(),
      response_id: generateResponseId(email, phone)
    };
    
    // Envoyer au backend avec retry
    sendToBackend(payload);
    
  } catch (error) {
    Logger.log('❌ Erreur critique: ' + error.toString());
    Logger.log('Stack trace: ' + error.stack);
    
    // Notification d'erreur (optionnel)
    try {
      MailApp.sendEmail({
        to: 'oragroup24@gmail.com',
        subject: '🔴 Erreur Auto-Responder',
        body: 'Erreur lors du traitement du formulaire:\n\n' + error.toString() + '\n\nStack:\n' + error.stack
      });
    } catch (e) {
      Logger.log('⚠️ Impossible d\'envoyer l\'email d\'erreur: ' + e.toString());
    }
  }
}


/**
 * Extrait les données du formulaire avec stratégie de fallback robuste
 * @param {Object} e - Objet événement
 * @return {Object} Données du formulaire normalisées
 */
function extractFormData(e) {
  Logger.log('🔍 Extraction des données (Type: ' + typeof e + ')');
  
  // Stratégie 1: e.namedValues (déclencheur standard)
  if (e && e.namedValues && Object.keys(e.namedValues).length > 0) {
    Logger.log('✅ Méthode 1: e.namedValues');
    return normalizeData(e.namedValues);
  }
  
  // Stratégie 2: e.response.getItemResponses()
  if (e && e.response) {
    try {
      Logger.log('🔄 Méthode 2: e.response.getItemResponses()');
      const items = e.response.getItemResponses();
      const data = {};
      items.forEach(function(item) {
        const title = item.getItem().getTitle();
        const response = item.getResponse();
        data[title] = Array.isArray(response) ? response : [response];
      });
      if (Object.keys(data).length > 0) {
        Logger.log('✅ Données extraites via e.response');
        return normalizeData(data);
      }
    } catch (err) {
      Logger.log('⚠️ Erreur méthode 2: ' + err.toString());
    }
  }
  
  // Stratégie 3: Récupérer la dernière réponse directement du formulaire
  try {
    Logger.log('🔄 Méthode 3: FormApp.getActiveForm()');
    const form = FormApp.getActiveForm();
    const responses = form.getResponses();
    
    if (responses.length > 0) {
      const lastResponse = responses[responses.length - 1];
      const items = lastResponse.getItemResponses();
      const data = {};
      
      items.forEach(function(item) {
        const title = item.getItem().getTitle();
        const response = item.getResponse();
        data[title] = Array.isArray(response) ? response : [response];
      });
      
      if (Object.keys(data).length > 0) {
        Logger.log('✅ Données extraites via FormApp (dernière réponse)');
        return normalizeData(data);
      }
    }
  } catch (err) {
    Logger.log('⚠️ Erreur méthode 3: ' + err.toString());
  }
  
  // Stratégie 4: Si e contient directement les données
  if (e && typeof e === 'object' && !e.namedValues && !e.response) {
    Logger.log('🔄 Méthode 4: Objet direct');
    return normalizeData(e);
  }
  
  Logger.log('❌ Aucune méthode d\'extraction n\'a fonctionné');
  return {};
}


/**
 * Normalise les données (tableaux → chaînes) - Version améliorée
 * @param {Object} data - Données brutes
 * @return {Object} Données normalisées
 */
function normalizeData(data) {
  const normalized = {};
  for (const key in data) {
    const value = data[key];
    
    if (Array.isArray(value)) {
      // Filtrer les valeurs vides et prendre la première valide
      const filtered = value.filter(function(v) { return v != null && v !== ''; });
      normalized[key] = filtered.length > 0 ? String(filtered[0]).trim() : '';
    } else {
      normalized[key] = value != null ? String(value).trim() : '';
    }
  }
  return normalized;
}


/**
 * Extrait un champ avec multiples variantes de noms (version optimisée avec scoring)
 * @param {Object} data - Données normalisées
 * @param {Array<string>} fieldNames - Liste des noms possibles (ordre de priorité)
 * @return {string} Valeur trouvée ou chaîne vide
 */
function extractField(data, fieldNames) {
  let bestMatch = { value: '', score: 0 };
  
  for (let i = 0; i < fieldNames.length; i++) {
    const fieldName = fieldNames[i];
    const priority = fieldNames.length - i;  // Premier nom = plus haute priorité
    
    for (const key in data) {
      const keyLower = key.toLowerCase();
      const fieldLower = fieldName.toLowerCase();
      let score = 0;
      
      // Score 1: Correspondance exacte (case-insensitive)
      if (keyLower === fieldLower) {
        score = 1000 + priority;
      }
      // Score 2: Correspondance exacte (avec espaces normalisés)
      else if (keyLower.replace(/\s+/g, ' ') === fieldLower.replace(/\s+/g, ' ')) {
        score = 900 + priority;
      }
      // Score 3: Le champ commence par le terme recherché
      else if (keyLower.startsWith(fieldLower)) {
        score = 500 + priority;
      }
      // Score 4: Le champ se termine par le terme recherché
      else if (keyLower.endsWith(fieldLower)) {
        score = 400 + priority;
      }
      // Score 5: Le terme est contenu (avec pénalité selon position)
      else if (keyLower.indexOf(fieldLower) !== -1) {
        const position = keyLower.indexOf(fieldLower);
        score = 200 + priority - position;
      }
      
      // Si ce match est meilleur, le garder
      if (score > bestMatch.score && data[key]) {
        bestMatch = {
          value: String(data[key]).trim(),
          score: score,
          matchedKey: key,
          searchTerm: fieldName
        };
      }
    }
  }
  
  // Log du meilleur match pour debugging
  if (bestMatch.score > 0) {
    Logger.log('🎯 Match trouvé: "' + bestMatch.matchedKey + '" (score: ' + bestMatch.score + ') pour "' + bestMatch.searchTerm + '"');
  }
  
  return bestMatch.value;
}


/**
 * Valide une adresse email
 * @param {string} email - Email à valider
 * @return {boolean} True si valide
 */
function isValidEmail(email) {
  if (!email) return false;
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}


/**
 * Valide un numéro de téléphone - Version assouplie
 * @param {string} phone - Téléphone à valider
 * @return {boolean} True si valide
 */
function isValidPhone(phone) {
  if (!phone) return false;
  // Accepte les numéros avec ou sans +, espaces, tirets, parenthèses, points
  const cleaned = phone.replace(/[\s\-\(\)\.]/g, '');
  // Doit contenir au moins 6 chiffres (permet numéros courts et services)
  // Maximum 20 chiffres (codes internationaux longs)
  return /^\+?[\d]{6,20}$/.test(cleaned);
}


/**
 * Nettoie une chaîne (trim + normalisation)
 * @param {string} str - Chaîne à nettoyer
 * @return {string} Chaîne nettoyée
 */
function cleanString(str) {
  if (!str) return '';
  return String(str).trim().replace(/\s+/g, ' ');
}


/**
 * Génère un ID unique pour la réponse
 * @param {string} email - Email
 * @param {string} phone - Téléphone
 * @return {string} ID unique
 */
function generateResponseId(email, phone) {
  const timestamp = new Date().getTime();
  const data = email + phone + timestamp;
  // Simple hash (pour ID unique, pas pour sécurité)
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36);
}


/**
 * Envoie les données au backend avec retry
 * @param {Object} payload - Données à envoyer
 */
function sendToBackend(payload) {
  const maxRetries = 3;
  let attempt = 0;
  
  while (attempt < maxRetries) {
    attempt++;
    
    try {
      Logger.log('📤 Tentative ' + attempt + '/' + maxRetries + ' - Envoi au backend...');
      
      const options = {
        method: 'post',
        contentType: 'application/json',
        headers: {
          'Authorization': 'Bearer ' + SECRET_KEY,
          'User-Agent': 'Google-Apps-Script/1.0'
        },
        payload: JSON.stringify(payload),
        muteHttpExceptions: true,
        timeout: 60000  // 60 secondes
      };
      
      const response = UrlFetchApp.fetch(SERVER_URL + '/api/receive', options);
      const responseCode = response.getResponseCode();
      const responseText = response.getContentText();
      
      Logger.log('📥 Code HTTP: ' + responseCode);
      Logger.log('📥 Réponse: ' + responseText);
      
      if (responseCode >= 200 && responseCode < 300) {
        Logger.log('✅ Succès ! Email et SMS envoyés.');
        return true;
      } else if (responseCode === 401) {
        Logger.log('🔒 Erreur d\'authentification - Vérifiez SECRET_KEY');
        return false;  // Pas de retry pour erreur d'auth
      } else if (responseCode >= 500) {
        Logger.log('⚠️ Erreur serveur ' + responseCode + ' - Retry dans 2s...');
        Utilities.sleep(2000);
        continue;
      } else {
        Logger.log('⚠️ Erreur client ' + responseCode + ': ' + responseText);
        return false;
      }
      
    } catch (error) {
      Logger.log('❌ Erreur réseau (tentative ' + attempt + '): ' + error.toString());
      
      if (attempt < maxRetries) {
        Logger.log('⏳ Retry dans ' + (attempt * 2) + ' secondes...');
        Utilities.sleep(attempt * 2000);
      }
    }
  }
  
  Logger.log('❌ Échec après ' + maxRetries + ' tentatives');
  return false;
}


/**
 * Fonction utilitaire pour extraire une valeur d'un champ (legacy - gardée pour compatibilité)
 * @param {Object} namedValues - Objet contenant toutes les réponses
 * @param {string} fieldName - Nom du champ à extraire
 * @return {string} La valeur du champ ou chaîne vide
 */
function getFieldValue(namedValues, fieldName) {
  return extractField(namedValues, [fieldName]);
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
