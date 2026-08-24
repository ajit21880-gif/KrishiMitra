import os
import requests
from typing import Dict, Any, Optional

class WhatsAppService:
    @staticmethod
    def send_via_twilio(to_number: str, body: str) -> bool:
        """Sends WhatsApp message via Twilio API"""
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886") # Twilio sandbox number
        
        if not account_sid or not auth_token:
            print(f"[SIMULATED TWILIO OUTBOUND] To: {to_number} | Body: {body}")
            return True
            
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        # Ensure correct formatting
        if not to_number.startswith("whatsapp:"):
            to_formatted = f"whatsapp:{to_number}"
        else:
            to_formatted = to_number
            
        payload = {
            "From": from_number,
            "To": to_formatted,
            "Body": body
        }
        
        try:
            response = requests.post(url, data=payload, auth=(account_sid, auth_token), timeout=8)
            if response.status_code in [200, 201]:
                print(f"Twilio message sent successfully to {to_number}")
                return True
            else:
                print(f"Twilio error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Error calling Twilio: {e}")
            return False

    @staticmethod
    def send_via_meta(to_number: str, body: str) -> bool:
        """Sends WhatsApp message via direct Meta Cloud API"""
        phone_number_id = os.environ.get("META_PHONE_NUMBER_ID")
        access_token = os.environ.get("META_ACCESS_TOKEN")
        
        if not phone_number_id or not access_token:
            print(f"[SIMULATED META OUTBOUND] To: {to_number} | Body: {body}")
            return True
            
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Strip "whatsapp:" prefix if present
        clean_number = to_number.replace("whatsapp:", "").replace("+", "").strip()
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_number,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": body
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=8)
            if response.status_code in [200, 201]:
                print(f"Meta message sent successfully to {to_number}")
                return True
            else:
                print(f"Meta error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Error calling Meta WhatsApp API: {e}")
            return False

    @classmethod
    def send_message(cls, to_number: str, body: str) -> bool:
        """
        Sends WhatsApp message. Dynamically selects provider based on config.
        Default provider is Twilio, but switches to Meta if configured or requested.
        """
        provider = os.environ.get("WHATSAPP_PROVIDER", "twilio").lower()
        if provider == "meta":
            return cls.send_via_meta(to_number, body)
        else:
            return cls.send_via_twilio(to_number, body)
