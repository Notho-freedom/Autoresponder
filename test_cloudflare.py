import requests
import time
import json

print("🧪 Tests du serveur Auto-Responder\n")
print("=" * 60)

# Test 1: Local endpoint
print("\n1️⃣  Test endpoint local (http://localhost:8000/api/status)")
print("-" * 60)
try:
    response = requests.get("http://localhost:8000/api/status", timeout=5)
    print(f"✅ Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: Cloudflare URL
print("\n" + "=" * 60)
print("\n2️⃣  Test URL Cloudflare publique")
print("-" * 60)
try:
    url = "https://blowing-perfect-choir-spectrum.trycloudflare.com/api/status"
    print(f"Testing: {url}")
    response = requests.get(url, timeout=10)
    print(f"✅ Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3: Test webhook avec données
print("\n" + "=" * 60)
print("\n3️⃣  Test webhook /api/receive (avec données de test)")
print("-" * 60)
try:
    headers = {
        "Authorization": "Bearer your_secret_key_for_webhook_authentication",
        "Content-Type": "application/json"
    }
    
    data = {
        "email": "test@example.com",
        "phone": "+33612345678",
        "name": "Test User",
        "timestamp": "2025-11-09T10:00:00Z"
    }
    
    response = requests.post(
        "http://localhost:8000/api/receive",
        headers=headers,
        json=data,
        timeout=10
    )
    print(f"✅ Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("\n✅ Tests terminés!")
