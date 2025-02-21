import psutil
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv, find_dotenv

# Intervalo de monitoreo en segundos
INTERVAL = 1
ADMIN_AVISADO = False

# ==============================
# 📌 Función para enviar correos
# ==============================
def envioCorreo():
    """Envía un correo cuando se detecta una anomalía en el consumo de red."""
    dotenv_path = find_dotenv()
    if dotenv_path == "":
        print("❌ Archivo .env no encontrado")
        return  # Salimos de la función si no se encuentra el .env
    else:
        print(f"✅ Archivo .env cargado desde: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)

    # Configuración del servidor SMTP y credenciales
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = os.getenv("EMAIL_SENDER")  # Email del remitente
    SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Contraseña del remitente
    RECEIVER_EMAIL = "hola34luis@gmail.com"  # Email del destinatario

    # Contenido del email
    subject = "⚠ Anomalía detectada en el servidor"
    body = """
    Hola,

    Se ha detectado un consumo anormal en la red del servidor.

    Revisa la situación lo antes posible.

    Saludos,
    Sistema de Monitoreo
    """

    try:
        # Crear el correo
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Activar TLS
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Enviar el email
        server.send_message(message)
        print("✅ Correo enviado con éxito!")

        # Cerrar conexión
        server.quit()
    
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")

# ===================================
# 📌 Función para medir el uso de red
# ===================================
def get_network_usage(interval):
    """Calcula el uso de la red en bytes/s en un intervalo de tiempo."""
    initial_net_io = psutil.net_io_counters()
    time.sleep(interval)
    net_io = psutil.net_io_counters()
    subida = (net_io.bytes_sent - initial_net_io.bytes_sent) / interval
    descarga = (net_io.bytes_recv - initial_net_io.bytes_recv) / interval
    return subida, descarga

# =======================================
# 📌 Obtención de valores de referencia
# =======================================
if not os.path.exists("red.txt"):
    print("📊 Calculando valores normales de red...")

    # Promediamos los valores en 10 segundos
    total_subida = 0
    total_descarga = 0
    for _ in range(10):
        s, d = get_network_usage(INTERVAL)
        total_subida += s
        total_descarga += d

    subida = total_subida / 10
    descarga = total_descarga / 10

    # Guardamos los valores en el archivo red.txt
    with open("red.txt", 'w') as archivo:
        archivo.write(f"{subida},{descarga}")
    
    print(f"✅ Valores guardados: Subida={subida:.2f} bytes/s, Descarga={descarga:.2f} bytes/s")

else:
    # Cargar valores de referencia desde el archivo
    with open("red.txt", 'r') as archivo:
        linea = archivo.readline()
    
    partido = linea.split(",")
    subida = float(partido[0])
    descarga = float(partido[1])

print(f"📈 Valores normales cargados: Subida={subida:.2f} bytes/s, Descarga={descarga:.2f} bytes/s")

# ===================================
# 📌 Monitoreo de uso de red en vivo
# ===================================
previous_net_io = psutil.net_io_counters()

while True:
    # Leer los contadores de red actuales
    current_net_io = psutil.net_io_counters()

    # Calcular uso de red en el intervalo
    nuevasubida = (current_net_io.bytes_sent - previous_net_io.bytes_sent) / INTERVAL
    nuevadescarga = (current_net_io.bytes_recv - previous_net_io.bytes_recv) / INTERVAL

    # Actualizar el valor anterior
    previous_net_io = current_net_io

    # Verificar anomalías
    if nuevasubida > subida * 15 or nuevadescarga > descarga * 15:
        print(f"⚠ Anomalía detectada: Subida={nuevasubida:.2f} bytes/s, Descarga={nuevadescarga:.2f} bytes/s")
        
        if not ADMIN_AVISADO:
            # envioCorreo()
            print("🚨 (Simulación) Hubiera enviado un correo")
            ADMIN_AVISADO = True  # Evitar enviar múltiples correos seguidos
    
    else:
        print(f"✅ Normal: Subida={nuevasubida:.2f} bytes/s, Descarga={nuevadescarga:.2f} bytes/s")

    # Esperar el intervalo antes de la próxima medición
    time.sleep(INTERVAL)
