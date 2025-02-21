import os               # Para acceder a variables de entorno
import psutil           # Para obtener estadísticas de red
import time             # Para manejar intervalos y tiempos de espera
import smtplib          # Para enviar correos electrónicos
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, find_dotenv

# Intervalo de tiempo (en segundos) entre mediciones
INTERVAL = 1
# Umbral para detectar anomalías (15 veces el valor normal)
ANOMALY_THRESHOLD = 15
# Bandera para evitar enviar múltiples correos en una misma anomalía
admin_avisado = False

# Carga el archivo .env para obtener las credenciales
dotenv_path = find_dotenv()
if dotenv_path == "":
    print("❌ Archivo .env no encontrado")
else:
    print(f"✅ Archivo .env cargado desde: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)

# Configuración del servidor SMTP y credenciales de correo
SMTP_SERVER = "smtp.gmail.com"  # Servidor SMTP de Gmail
SMTP_PORT = 587                 # Puerto SMTP para TLS
SENDER_EMAIL = os.getenv("EMAIL_SENDER")      # Email del remitente
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD") # Contraseña del remitente
RECEIVER_EMAIL = "hortiguelavaliente@gmail.com" # Email del destinatario

def send_email():
    """
    Envía un correo electrónico para alertar sobre una anomalía en el uso de la red.
    Utiliza SMTP con cifrado TLS.
    """
    subject = "Anomalía detectada"
    body = (
        "Hola,\n\n"
        "Se ha detectado un consumo anormal en tu servidor.\n\n"
        "Saludos,\n"
        "Javier"
    )
    try:
        # Crear el mensaje de correo
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # Conectar al servidor SMTP y enviar el mensaje
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Inicia la encriptación TLS
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)
        print("✅ Email enviado exitosamente!")
        server.quit()
    except Exception as e:
        print(f"❌ Error al enviar el email: {e}")

def get_network_usage(interval):
    """
    Mide la velocidad de subida y bajada en un intervalo dado.

    Parámetros:
        interval (float): Tiempo en segundos para la medición.

    Retorna:
        tuple: (upload_rate, download_rate) en bytes por segundo.
    """
    initial_net_io = psutil.net_io_counters()
    time.sleep(interval)
    net_io = psutil.net_io_counters()
    upload_rate = (net_io.bytes_sent - initial_net_io.bytes_sent) / interval
    download_rate = (net_io.bytes_recv - initial_net_io.bytes_recv) / interval
    return upload_rate, download_rate

# Cálculo del baseline (valores normales) sobre 10 mediciones
print("Empezamos el cálculo de valores normales (baseline)...")
total_upload = 0
total_download = 0
baseline_iterations = 10

for i in range(baseline_iterations):
    up, down = get_network_usage(INTERVAL)
    total_upload += up
    total_download += down
    print(f"Medición {i+1}/{baseline_iterations}: Subida = {up:.2f} bytes/s, Descarga = {down:.2f} bytes/s")

baseline_upload = total_upload / baseline_iterations
baseline_download = total_download / baseline_iterations

print(f"\nValores normales: Subida = {baseline_upload:.2f} bytes/s, Descarga = {baseline_download:.2f} bytes/s")
print("Ahora comenzamos la toma de datos...\n")

# Monitoreo en tiempo real de la red para detectar anomalías
previous_net_io = psutil.net_io_counters()

while True:
    current_net_io = psutil.net_io_counters()
    # Calcula la velocidad en el intervalo actual
    current_upload = (current_net_io.bytes_sent - previous_net_io.bytes_sent) / INTERVAL
    current_download = (current_net_io.bytes_recv - previous_net_io.bytes_recv) / INTERVAL
    # Actualiza los contadores para la siguiente medición
    previous_net_io = current_net_io
    
    # Verifica si la velocidad actual supera el umbral definido (baseline * ANOMALY_THRESHOLD)
    if current_upload > baseline_upload * ANOMALY_THRESHOLD or current_download > baseline_download * ANOMALY_THRESHOLD:
        print(f"🚨 Anomalía detectada: Subida = {current_upload:.2f} bytes/s, Descarga = {current_download:.2f} bytes/s")
        # Si aún no se ha enviado la alerta, se envía el correo
        if not admin_avisado:
            send_email()
            admin_avisado = True
    else:
        print(f"Normal: Subida = {current_upload:.2f} bytes/s, Descarga = {current_download:.2f} bytes/s")
    
    time.sleep(INTERVAL)

ca