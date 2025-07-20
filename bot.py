import os
from flask import Flask, request
import requests
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

app = Flask(__name__)

# Get credentials from environment
GREENAPI_INSTANCE_ID = os.getenv("GREENAPI_INSTANCE_ID")
GREENAPI_TOKEN = os.getenv("GREENAPI_TOKEN")

# Hugging Face model endpoint (can be customized)
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

@app.route("/", methods=["GET"])
def home():
    return "Green API WhatsApp Bot is Live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        message = data["data"]["body"]
        sender = data["data"]["from"]
    except KeyError:
        return "Invalid message structure", 400

    # Send the message to Hugging Face for a response
    reply = get_bot_reply(message)

    # Send response via Green API
    send_whatsapp_message(sender, reply)

    return "OK", 200

def get_bot_reply(message):
    headers = {"Content-Type": "application/json"}
    payload = {"inputs": {"text": message}}

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        result = response.json()
        reply = result.get("generated_text", "Sorry, I couldn't understand that.")
    except Exception as e:
        reply = f"Error: {str(e)}"

    return reply

def send_whatsapp_message(to, message):
    url = f"https://7105.api.greenapi.com/waInstance{GREENAPI_INSTANCE_ID}/sendMessage/{GREENAPI_TOKEN}"
    payload = {
        "chatId": to,
        "message": message
    }

    response = requests.post(url, json=payload)
    print("Green API Response:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(debug=True)
