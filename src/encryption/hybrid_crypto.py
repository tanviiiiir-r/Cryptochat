from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import hmac
import hashlib

# ------------------ RSA KEYS ------------------

def generate_rsa_keypair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    with open("rsa_private.pem", "wb") as priv_file:
        priv_file.write(private_key)

    with open("rsa_public.pem", "wb") as pub_file:
        pub_file.write(public_key)

    print("[+] RSA Key Pair Generated")

# ------------------ ENCRYPTION ------------------

def encrypt_message(message, public_key_path="rsa_public.pem"):
    # Load public key
    with open(public_key_path, "rb") as f:
        public_key = RSA.import_key(f.read())

    # Generate AES key
    aes_key = get_random_bytes(16)  # 128-bit AES

    # Encrypt message with AES
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode())

    # Encrypt AES key with RSA
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_aes_key = cipher_rsa.encrypt(aes_key)

    # Create HMAC of ciphertext using AES key
    message_hmac = generate_hmac(ciphertext, aes_key)

    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(cipher_aes.nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
        "enc_aes_key": base64.b64encode(enc_aes_key).decode(),
        "hmac": base64.b64encode(message_hmac).decode()
    }

# ------------------ DECRYPTION ------------------

def decrypt_message(enc_data, private_key_path="rsa_private.pem"):
    # Load private key
    with open(private_key_path, "rb") as f:
        private_key = RSA.import_key(f.read())

    # Decode base64
    ciphertext = base64.b64decode(enc_data["ciphertext"])
    nonce = base64.b64decode(enc_data["nonce"])
    tag = base64.b64decode(enc_data["tag"])
    enc_aes_key = base64.b64decode(enc_data["enc_aes_key"])
    received_hmac = base64.b64decode(enc_data["hmac"])

    # Decrypt AES key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(enc_aes_key)

    # Verify HMAC before decryption
    if not verify_hmac(ciphertext, aes_key, received_hmac):
        print("[!] HMAC mismatch detected!")
        print("Received HMAC:", received_hmac.hex())
        print("Computed HMAC:", generate_hmac(ciphertext, aes_key).hex())
        raise ValueError("Message integrity check failed! Tampered or corrupted.")

    # Decrypt message
    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce)

    # Use this for full integrity check with AES tag
    message = cipher_aes.decrypt_and_verify(ciphertext, tag)

    # For debugging only (comment the above and uncomment below to bypass AES tag)
    # message = cipher_aes.decrypt(ciphertext)

    return message.decode()

# ------------------ HMAC FUNCTIONS ------------------

def generate_hmac(data: bytes, key: bytes):
    return hmac.new(key, data, hashlib.sha256).digest()

def verify_hmac(data: bytes, key: bytes, received_hmac: bytes):
    computed = generate_hmac(data, key)
    return hmac.compare_digest(computed, received_hmac)
