"""
Script de test pour vérifier que le serveur fonctionne
"""
import requests
import json

def test_status():
    """Test de l'endpoint /api/status"""
    try:
        response = requests.get("http://localhost:8000/api/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_webhook():
    """Test de l'endpoint /api/receive avec données de test"""
    headers = {
        "Authorization": "Bearer your_secret_key_here",
        "Content-Type": "application/json"
    }
    
    data = {
        "response_id": "test_" + str(int(requests.get("http://localhost:8000/api/status").json()["timestamp"])),
        "email": "test@example.com",
        "phone": "+33612345678",
        "name": "Test User",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/receive",
            headers=headers,
            json=data
        )
        print(f"\nWebhook Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test du serveur Auto-Responder\n")
    print("=" * 50)
    
    # Test 1: Status endpoint
    print("\n1️⃣  Test de l'endpoint /api/status")
    print("-" * 50)
    if test_status():
        print("✅ Le serveur répond correctement!")
    else:
        print("❌ Le serveur ne répond pas")
        exit(1)
    
    # Test 2: Webhook endpoint (optionnel)
    print("\n" + "=" * 50)
    print("\n2️⃣  Test de l'endpoint /api/receive (optionnel)")
    print("-" * 50)
    print("Note: Pour tester le webhook, configurez d'abord votre .env avec:")
    print("  - SECRET_KEY")
    print("  - SMTP credentials")
    print("  - Twilio credentials")
    print("\nAppuyez sur Entrée pour continuer ou Ctrl+C pour arrêter...")
    input()
    
    if test_webhook():
        print("✅ Le webhook fonctionne!")
    else:
        print("⚠️  Le webhook a échoué (vérifiez vos credentials)")
