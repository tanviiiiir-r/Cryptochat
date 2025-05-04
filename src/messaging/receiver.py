from src.encryption.hybrid_crypto import decrypt_message
import json
import os
from datetime import datetime

def receive_message(my_username):
    filename = f"messages/{my_username}.msg"

    if not os.path.exists(filename):
        print("[-] No message found.")
        return

    with open(filename, "r") as f:
        data = json.load(f)

    encrypted = data["message"]
    read_once = data.get("read_once", False)
    expiry_utc = data.get("expiry_utc", None)

    # Check expiration time
    if expiry_utc:
        expiry_time = datetime.fromisoformat(expiry_utc)
        if datetime.utcnow() > expiry_time:
            os.remove(filename)
            print("[-] Message has expired and was deleted automatically ⏳💥")
            return

    try:
        decrypted = decrypt_message(encrypted)
        print(f"[+] New secure message:\n{decrypted}")

        if read_once:
            os.remove(filename)
            print(f"[+] Message self-destructed after reading 🔥")

    except Exception as e:
        print("[-] Failed to decrypt message:", str(e))
