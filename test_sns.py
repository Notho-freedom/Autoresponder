"""Test script pour AWS SNS"""
import os
from dotenv import load_dotenv
load_dotenv()

from services.aws_sns_service import AWSSNSService

print("=== TEST AWS SNS ===\n")

# Initialiser le service
sns = AWSSNSService()
print(f"✓ Service initialized: {sns.client is not None}")
print(f"✓ Region: {sns.aws_region}")
print(f"✓ Sender ID: {sns.sender_id}")

# Test de connexion
print("\n--- Connection Test ---")
result = sns.test_connection()
print(f"Connection: {'✓ OK' if result else '✗ FAILED'}")

if result:
    # Informations sur le quota
    print("\n--- Monthly Spend Info ---")
    spend = sns.get_monthly_spend()
    print(f"Monthly Limit: ${spend.get('MonthlySpendLimit', 'N/A')}")
    
    # Test d'envoi SMS
    print("\n--- Test SMS Envoi ---")
    test_phone = "+35795184406"
    test_message = "Test AWS SNS - Nkeng Analytics"
    
    confirm = input(f"Envoyer SMS de test à {test_phone}? (y/n): ")
    if confirm.lower() == 'y':
        success = sns.send_sms(test_phone, test_message)
        print(f"Envoi SMS: {'✓ SUCCESS' if success else '✗ FAILED'}")
else:
    print("\n✗ Impossible de tester l'envoi - connexion échouée")
    print("Vérifier:")
    print("  1. AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY corrects")
    print("  2. Permissions IAM (SNSPublish)")
    print("  3. Quota SMS configuré dans AWS console")
