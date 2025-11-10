"""Test complet - Brevo + Vonage"""
import os
from dotenv import load_dotenv
load_dotenv()

from services.brevo_email_service import BrevoEmailService
from services.vonage_sms_service import VonageSMSService

print("=== TEST STACK PRODUCTION BREVO ===\n")

# Services
email = BrevoEmailService()
sms = VonageSMSService()

# Test Email
print("--- Email via Brevo ---")
email_result = email.send_confirmation_email('bobymomo6@gmail.com', 'Boby Test Brevo')
print(f"Email: {'✓ ENVOYÉ' if email_result else '✗ ÉCHEC'}\n")

# Test SMS
print("--- SMS via Vonage ---")
sms_result = sms.send_confirmation_sms('+35795184406', 'Boby Test Brevo')
print(f"SMS: {'✓ ENVOYÉ' if sms_result else '✗ ÉCHEC'}")
