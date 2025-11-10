"""Test Brevo Email Service"""
import os
from dotenv import load_dotenv
load_dotenv()

from services.brevo_email_service import BrevoEmailService

print("=== TEST BREVO EMAIL ===\n")

brevo = BrevoEmailService()

# 1. Test connexion
print("--- Connexion & Compte ---")
if brevo.test_connection():
    account_info = brevo.get_account_info()
    print(f"Email compte: {account_info.get('email', 'N/A')}")
    print(f"Société: {account_info.get('companyName', 'N/A')}")
    
    # Plan info
    plan = account_info.get('plan', [{}])[0] if account_info.get('plan') else {}
    print(f"Plan: {plan.get('type', 'N/A')}")
    print(f"Crédits email: {plan.get('credits', 'N/A')}\n")
else:
    print("✗ Échec connexion\n")
    exit(1)

# 2. Test d'envoi (optionnel)
send_test = input("Envoyer un email test à bobymomo6@gmail.com ? (y/n): ")
if send_test.lower() == 'y':
    print("\n--- Envoi Email ---")
    
    # Test API
    print("Mode API:")
    result_api = brevo.send_email_api(
        'bobymomo6@gmail.com',
        'Test Brevo API - Autoresponder',
        '<h1>Test Brevo</h1><p>Email envoyé via API Brevo!</p>',
        'Boby'
    )
    print(f"API: {'✓ ENVOYÉ' if result_api else '✗ ÉCHEC'}")
    
    # Test SMTP
    print("\nMode SMTP:")
    result_smtp = brevo.send_email_smtp(
        'bobymomo6@gmail.com',
        'Test Brevo SMTP - Autoresponder',
        '<h1>Test Brevo</h1><p>Email envoyé via SMTP Brevo!</p>',
        'Boby'
    )
    print(f"SMTP: {'✓ ENVOYÉ' if result_smtp else '✗ ÉCHEC'}")
