"""Test complet - SendGrid + Vonage"""
import os
from dotenv import load_dotenv
load_dotenv()

from services.email_service import EmailService
from services.vonage_sms_service import VonageSMSService

print("=== TEST SERVICES PRODUCTION ===\n")

# Services
email = EmailService()
sms = VonageSMSService()

# Test Email
print("--- Email via SendGrid ---")
email_result = email.send_confirmation_email('bobymomo6@gmail.com', 'Boby Test SendGrid')
print(f"Email: {'✓ ENVOYÉ' if email_result else '✗ ÉCHEC'}\n")

# Test SMS
print("--- SMS via Vonage ---")
sms_result = sms.send_confirmation_sms('+35795184406', 'Boby Test Vonage')
print(f"SMS: {'✓ ENVOYÉ' if sms_result else '✗ ÉCHEC'}")
