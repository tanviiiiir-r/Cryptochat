# 🛡️ Cryptochat: Security Architecture Report

This report outlines the cryptographic architecture and implementation details of **Cryptochat**, a secure messaging application developed with Python and PyQt5. It is designed to demonstrate modern secure communication practices and provide academic-grade protection through hybrid encryption.

---

## 🔐 Hybrid Encryption Overview

Cryptochat uses a hybrid encryption model, combining:

* **Asymmetric RSA (2048-bit)** for secure key exchange
* **Symmetric AES (128-bit, EAX mode)** for fast and secure message encryption
* **HMAC-SHA256** for verifying integrity

This architecture balances performance, security, and portability.

---

## 🔒 Key Management

* RSA key pairs are generated per user:

  * `rsa_private.pem`
  * `rsa_public.pem`
* Keys are stored locally and never transmitted
* The AES session key is randomly generated per message

---

## ✨ Message Encryption Flow

1. **Generate a random AES key** for each message
2. **Encrypt the plaintext** using AES in EAX mode (provides confidentiality + authentication tag)
3. **Encrypt the AES key** using the recipient's RSA public key (PKCS1\_OAEP)
4. **Generate an HMAC** over the AES ciphertext using the AES key
5. Store all encrypted components (AES key, ciphertext, tag, nonce, HMAC) in a message file

---

## 🔍 Message Decryption Flow

1. Decrypt AES key using the RSA private key
2. Verify HMAC to ensure ciphertext integrity
3. Decrypt AES ciphertext using EAX mode
4. Check tag to verify authenticity
5. Display plaintext message to the recipient

---

## ⏳ Message Self-Destruction Logic

* Each message has a UTC-based expiry timestamp
* Files are deleted on read or after expiry, whichever comes first
* HMAC mismatch or AES tag failure triggers a security exception

---

## 🔏 Threat Model Assumptions

| Threat                    | Mitigation                          |
| ------------------------- | ----------------------------------- |
| Message tampering         | HMAC-SHA256 over ciphertext         |
| Unauthorized decryption   | RSA key-based access control        |
| Eavesdropping / replay    | AES with random nonce per message   |
| Message leaks post-expiry | Auto-delete enforced via file logic |

---

## 🚀 Security Objectives Achieved

* **Confidentiality**: RSA + AES encryption
* **Integrity**: HMAC and AES authentication tag
* **Authenticity**: Only decryptable with the correct RSA private key
* **Forward Secrecy**: New AES key per message
* **Ephemeral Data**: Message files are deleted after use

---

## 🚀 Educational Value

This project was built as an Erasmus+ portfolio artifact and demonstrates:

* Proper hybrid cryptosystem architecture
* Safe local key storage and ephemeral key handling
* Ethical design for privacy-aware messaging
* Python implementation of applied cryptography using `pycryptodome`

---

## ✨ Summary

Cryptochat presents a clean and ethical model for secure communication apps, and serves as a practical and presentable cybersecurity portfolio piece for academic or professional review.

> Built with respect for digital privacy and strong encryption.
