from src.encryption.hybrid_crypto import encrypt_message
import json
import os
from datetime import datetime, timedelta

def send_message(to_username, message_text, expiry_minutes=10):
    encrypted = encrypt_message(message_text)

    # Add metadata
    expiry_time = (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat()

    encrypted_message = {
        "message": encrypted,
        "read_once": True,
        "expiry_utc": expiry_time  # self-destruct after this time
    }

    os.makedirs("messages", exist_ok=True)
    filename = f"messages/{to_username}.msg"

    with open(filename, "w") as f:
        json.dump(encrypted_message, f)

    print(f"[+] Message securely sent to {to_username} 🔐 (expires at {expiry_time} UTC)")
