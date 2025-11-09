import requests
import json

BASE_URL = "https://autoresponder-qkpe.onrender.com"

print("🧪 Tests du serveur Render Auto-Responder\n")
print("=" * 60)

# Test 1: Status endpoint
print("\n1️⃣  Test de l'endpoint /api/status")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/api/status", timeout=30)
    print(f"✅ Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except requests.exceptions.Timeout:
    print("❌ Timeout - Le serveur met trop de temps à répondre")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: Root endpoint
print("\n" + "=" * 60)
print("\n2️⃣  Test de l'endpoint racine /")
print("-" * 60)
try:
    response = requests.get(BASE_URL, timeout=30)
    print(f"✅ Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3: Webhook avec authentification invalide (doit retourner 401)
print("\n" + "=" * 60)
print("\n3️⃣  Test webhook sans authentification (devrait retourner 401)")
print("-" * 60)
try:
    data = {
        "email": "test@example.com",
        "phone": "+33612345678",
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/receive", json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        print("✅ Authentification correctement requise")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 4: Webhook avec authentification valide
print("\n" + "=" * 60)
print("\n4️⃣  Test webhook avec authentification")
print("-" * 60)
print("⚠️  Nécessite que SECRET_KEY soit configuré sur Render")
try:
    headers = {
        "Authorization": "Bearer your_secret_key_for_webhook_authentication",
        "Content-Type": "application/json"
    }
    
    data = {
        "email": "test@example.com",
        "phone": "+33612345678",
        "name": "Test Render User",
        "timestamp": "2025-11-09T12:00:00Z"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/receive",
        headers=headers,
        json=data,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Webhook fonctionne correctement!")
    elif response.status_code == 401:
        print("\n⚠️  SECRET_KEY non configuré ou incorrect sur Render")
    else:
        print(f"\n⚠️  Réponse inattendue: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ Timeout - Le serveur met trop de temps à traiter la requête")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("\n📋 Résumé des tests terminés!")
print("\nSi vous voyez des erreurs de configuration:")
print("1. Vérifiez les variables d'environnement sur Render")
print("2. Assurez-vous que FIREBASE_CREDENTIALS_JSON est configuré")
print("3. Vérifiez SMTP_PASSWORD et TWILIO_AUTH_TOKEN")
