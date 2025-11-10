"""Test envoi à l'équipe dev"""
import os
from dotenv import load_dotenv
load_dotenv()

from services.email_service import EmailService
from services.vonage_sms_service import VonageSMSService

print("=== TEST ENVOI ÉQUIPE DEV ===\n")

email_service = EmailService()
sms_service = VonageSMSService()

# Liste des devs à tester
devs = [
    {
        "name": "Ousmane",
        "email": "ousmanemfochive4@mail.com",
        "phone": "+237658865868"
    },
    {
        "name": "Wilfrid",
        "email": "nzomutchawilfrid@gmail.com",
        "phone": "+237651881464"
    }
]

for dev in devs:
    print(f"--- Test pour {dev['name']} ---")
    
    # Email
    email_result = email_service.send_confirmation_email(dev['email'], dev['name'])
    print(f"Email ({dev['email']}): {'✓ ENVOYÉ' if email_result else '✗ ÉCHEC'}")
    
    # SMS
    sms_result = sms_service.send_confirmation_sms(dev['phone'], dev['name'])
    print(f"SMS ({dev['phone']}): {'✓ ENVOYÉ' if sms_result else '✗ ÉCHEC'}")
    print()

print("✅ Tests terminés!")
