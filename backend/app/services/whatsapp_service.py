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
#         return {"error": str(e)}



from twilio.rest import Client
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to: str, message: str):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        return {"sid": msg.sid, "status": msg.status}
    except Exception as e:
        # Print full error in terminal for debugging
        print(f"❌ WhatsApp send error: {e}")
        # Still return gracefully (don't crash API)
        return {"sid": None, "status": "failed", "error": str(e)}
