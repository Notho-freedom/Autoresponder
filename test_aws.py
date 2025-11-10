"""Test script pour AWS SES et SNS"""
import os
from dotenv import load_dotenv
load_dotenv()

from services.aws_ses_service import AWSSESService
from services.aws_sns_service import AWSSNSService

print("=== TEST BRANCHE AWS ===\n")

# Test AWS SES
print("--- AWS SES (Email) ---")
ses = AWSSESService()
print(f"✓ Service initialized: {ses.client is not None}")
print(f"✓ From: {ses.from_email}")
print(f"✓ Region: {ses.aws_region}")

ses_ok = ses.test_connection()
print(f"Connection: {'✓ OK' if ses_ok else '✗ FAILED'}")

if ses_ok:
    stats = ses.get_send_statistics()
    print(f"Quota: {stats.get('SentLast24Hours', 0)}/{stats.get('Max24HourSend', 0)} emails/24h")

# Test AWS SNS
print("\n--- AWS SNS (SMS) ---")
sns = AWSSNSService()
print(f"✓ Service initialized: {sns.client is not None}")
print(f"✓ Sender ID: {sns.sender_id}")
print(f"✓ Region: {sns.aws_region}")

sns_ok = sns.test_connection()
print(f"Connection: {'✓ OK' if sns_ok else '✗ FAILED'}")

if sns_ok:
    spend = sns.get_monthly_spend()
    print(f"Monthly Limit: ${spend.get('MonthlySpendLimit', 'N/A')}")

# Test envoi
if ses_ok and sns_ok:
    print("\n--- Test Envoi ---")
    test_email = "bobymomo6@gmail.com"
    test_phone = "+35795184406"
    
    confirm = input(f"Envoyer test email+SMS à {test_email}/{test_phone}? (y/n): ")
    if confirm.lower() == 'y':
        email_sent = ses.send_confirmation_email(test_email, "Boby Test AWS")
        sms_sent = sns.send_confirmation_sms(test_phone, "Boby Test AWS")
        
        print(f"Email: {'✓ SENT' if email_sent else '✗ FAILED'}")
        print(f"SMS: {'✓ SENT' if sms_sent else '✗ FAILED'}")
else:
    print("\n✗ Connexion échouée - vérifier credentials AWS")
