import socket
import threading
import json
import os
from datetime import datetime

class TCPServer:
    def __init__(self, config_file='server_config.json'):
        self.config = self.load_config(config_file)
        self.lock = threading.Lock()
        self.running = False
        
    def load_config(self, config_file):
        """Carga y valida la configuración del servidor"""
        default_config = {
            "host": "localhost",
            "port": 808,
            "log_file": "server.log",
            "max_connections": 5,
            "message_file": "messages.txt"
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Combinar con valores por defecto
            return {**default_config, **config}
            
        except FileNotFoundError:
            print(f"Archivo de configuración {config_file} no encontrado, usando valores por defecto")
            return default_config
        except json.JSONDecodeError:
            print("Error en formato del archivo de configuración, usando valores por defecto")
            return default_config

    def log_activity(self, message):
        """Registra actividad en el archivo de log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        with self.lock:
            with open(self.config['log_file'], 'a') as f:
                f.write(log_entry)

    def handle_client(self, conn, addr):
        """Maneja la conexión con un cliente"""
        self.log_activity(f"Conexión establecida desde {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                self.process_message(message, addr)
                
                response = f"Mensaje recibido: {message}"
                conn.sendall(response.encode('utf-8'))
                
        except ConnectionResetError:
            self.log_activity(f"Conexión con {addr} reseteada")
        finally:
            conn.close()
            self.log_activity(f"Conexión con {addr} cerrada")

    def process_message(self, message, addr):
        """Procesa y almacena los mensajes recibidos"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"{timestamp} | {addr[0]} | {message}\n"
        
        with self.lock:
            with open(self.config['message_file'], 'a') as f:
                f.write(entry)
        
        self.log_activity(f"Mensaje de {addr[0]}: {message}")

    def start(self):
        """Inicia el servidor"""
        self.running = True
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.config['host'], self.config['port']))
                s.listen(self.config['max_connections'])
                
                self.log_activity(f"Servidor iniciado en {self.config['host']}:{self.config['port']}")
                print(f"Servidor escuchando en {self.config['host']}:{self.config['port']}")
                
                while self.running:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                    thread.start()
                    self.log_activity(f"Conexiones activas: {threading.active_count() - 1}")
                    
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.log_activity(f"Error crítico: {str(e)}")
            self.stop()

    def stop(self):
        """Detiene el servidor"""
        self.running = False
        self.log_activity("Servidor detenido")
        print("\nServidor detenido")

if __name__ == "__main__":
    server = TCPServer()
    server.start()