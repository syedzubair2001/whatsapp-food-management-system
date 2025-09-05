

# from twilio.rest import Client
# from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# def send_whatsapp_message(to: str, message: str):
#     try:
#         msg = client.messages.create(
#             body=message,
#             from_=TWILIO_PHONE_NUMBER,
#             to=to
#         )
#         return {"sid": msg.sid, "status": msg.status}
#     except Exception as e:
#         # Print full error in terminal for debugging
#         print(f"❌ WhatsApp send error: {e}")
#         # Still return gracefully (don't crash API)
#         return {"sid": None, "status": "failed", "error": str(e)}




# app/services/whatsapp_service.py

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_whatsapp_message(to: str, message: str):
    """
    Send a WhatsApp message using Twilio.
    
    Parameters:
    - to: Recipient phone number (must include 'whatsapp:' prefix)
    - message: Message text
    
    Returns:
    - dict: { "sid": <message_sid>, "status": <status>, "error": <error_message_if_any> }
    """
    # Ensure the recipient number has 'whatsapp:' prefix
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"

    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        # Twilio returns 'queued', 'sent', 'delivered', etc. in msg.status
        return {"sid": msg.sid, "status": msg.status, "error": None}
    except Exception as e:
        # Print full error in terminal for debugging
        print(f"❌ WhatsApp send error: {e}")
        return {"sid": None, "status": "failed", "error": str(e)}
