"""Test final - Brevo Email + SMS"""
import os
from dotenv import load_dotenv
load_dotenv()

from services.brevo_email_service import BrevoEmailService
from services.brevo_sms_service import BrevoSMSService

print("=== TEST STACK BREVO (EMAIL + SMS) ===\n")

# Services
email = BrevoEmailService()
sms = BrevoSMSService()

# Test Email
print("--- Email via Brevo ---")
email_result = email.send_confirmation_email('bobymomo6@gmail.com', 'Boby')
print(f"Email: {'✓ ENVOYÉ' if email_result else '✗ ÉCHEC'}\n")

# Test SMS
print("--- SMS via Brevo ---")
sms_result = sms.send_confirmation_sms('+35795184406', 'Boby')
print(f"SMS: {'✓ ENVOYÉ' if sms_result else '✗ ÉCHEC'}")
