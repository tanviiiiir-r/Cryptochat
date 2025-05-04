import sys
import os
import json

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QTabWidget, QMessageBox
)
from PyQt5.QtCore import QTimer, QDateTime, Qt
from src.messaging.sender import send_message
from src.messaging.receiver import receive_message
from src.encryption.hybrid_crypto import generate_rsa_keypair
from datetime import datetime

# Generate RSA key pair if not exists
if not os.path.exists("rsa_private.pem") or not os.path.exists("rsa_public.pem"):
    generate_rsa_keypair()

class SendTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Recipient Username")

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your message here...")

        self.send_btn = QPushButton("Send Secure Message")
        self.send_btn.clicked.connect(self.send_message)

        layout.addWidget(QLabel("Recipient Username:"))
        layout.addWidget(self.user_input)
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)

    def send_message(self):
        user = self.user_input.text().strip()
        message = self.message_input.toPlainText().strip()
        if not user or not message:
            QMessageBox.warning(self, "Input Error", "Both username and message are required.")
            return
        send_message(user, message)
        QMessageBox.information(self, "Success", f"Message sent to {user} 🔐")
        self.user_input.clear()
        self.message_input.clear()

class ReceiveTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Your Username")

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)

        self.timer_label = QLabel("🕒 Message will disappear in: --:--")
        self.timer_label.setStyleSheet("color: red; font-weight: bold;")

        self.receive_btn = QPushButton("Receive & Decrypt")
        self.receive_btn.clicked.connect(self.receive_message)

        layout.addWidget(QLabel("Your Username:"))
        layout.addWidget(self.user_input)
        layout.addWidget(self.receive_btn)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

        # Timer setup
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = None

    def receive_message(self):
        user = self.user_input.text().strip()
        if not user:
            QMessageBox.warning(self, "Input Error", "Please enter your username.")
            return

        filename = f"messages/{user}.msg"
        if not os.path.exists(filename):
            QMessageBox.information(self, "Not Found", "No message found.")
            return

        try:
            with open(filename, "r") as f:
                data = json.load(f)

            expiry_utc = data.get("expiry_utc")
            if expiry_utc:
                expiry_dt = datetime.fromisoformat(expiry_utc)
                now = datetime.utcnow()
                self.remaining_seconds = int((expiry_dt - now).total_seconds())

                if self.remaining_seconds <= 0:
                    os.remove(filename)
                    QMessageBox.information(self, "Expired", "Message has expired and was deleted.")
                    self.output_area.clear()
                    self.timer.stop()
                    self.timer_label.setText("🕒 Message expired.")
                    return

                self.timer.start()

            # Capture output of receiver
            import io
            import sys
            from src.messaging.receiver import receive_message
            old_stdout = sys.stdout
            sys.stdout = mystdout = io.StringIO()
            receive_message(user)
            sys.stdout = old_stdout
            output = mystdout.getvalue()
            self.output_area.setPlainText(output)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_countdown(self):
        if self.remaining_seconds is not None:
            self.remaining_seconds -= 1
            if self.remaining_seconds <= 0:
                self.timer.stop()
                self.timer_label.setText("🕒 Message expired.")
                return

            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            self.timer_label.setText(f"🕒 Message will disappear in: {minutes:02d}:{seconds:02d}")

class CryptoChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cryptochat - Secure Messaging")
        self.resize(600, 400)

        tabs = QTabWidget()
        tabs.addTab(SendTab(), "Send")
        tabs.addTab(ReceiveTab(), "Receive")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

if __name__ == "__main__":
    import shutil

    try:
        app = QApplication(sys.argv)
        window = CryptoChatApp()
        window.show()
        app.exec_()
    finally:
        # Clean up messages folder on exit
        if os.path.exists("messages"):
            shutil.rmtree("messages")
            print("[+] All messages wiped securely on exit 🧹💥")


    
