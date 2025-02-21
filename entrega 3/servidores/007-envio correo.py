#!/usr/bin/env python3
"""
Script para enviar correos electrónicos de forma segura en Python usando SMTP.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
if dotenv_path == "":
    print("❌ Archivo .env no encontrado")
else:
    print(f"✅ Archivo .env cargado desde: {dotenv_path}")
    
    
load_dotenv(dotenv_path=dotenv_path)



# Cargar credenciales desde variables de entorno
SMTP_SERVER = "smtp.gmail.com"  # Servidor SMTP de Gmail
SMTP_PORT = 25   # Puerto SMTP para TLS
SENDER_EMAIL = os.getenv("EMAIL_SENDER")  # Email del remitente
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Contraseña del remitente
RECEIVER_EMAIL = "hola34luis@gmai.com"  # Email del destinatario

# Contenido del correo
SUBJECT = "Test Email from Python"
BODY = """
Hola,

Este es un correo de prueba enviado mediante la librería SMTP de Python.

Saludos,
Tu Nombre
"""

def send_email():
    """Envía un correo electrónico utilizando SMTP con autenticación segura."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ Error: Las credenciales de correo no están configuradas.")
        return
    
    try:
        # Crear el mensaje de correo
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = SUBJECT
        message.attach(MIMEText(BODY, "plain"))
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Iniciar cifrado TLS
        server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Autenticación
        
        # Enviar correo
        server.send_message(message)
        print("✅ Correo enviado correctamente!")
        
        server.quit()
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")

if __name__ == "__main__":
    send_email()
