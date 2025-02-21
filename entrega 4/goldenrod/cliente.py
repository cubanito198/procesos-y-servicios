import socket
import json
import sys
from colorama import Fore, Style, init

# Inicializar colores para la terminal
init(autoreset=True)

def load_config(config_path='client_config_sample.json'):
    """Carga la configuración del cliente"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_fields = ['server_host', 'server_port']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Falta el campo requerido: {field}")
        
        return config
    except Exception as e:
        print(f"{Fore.RED}Error de configuración: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

class SimpleTCPClient:
    def __init__(self):
        self.config = load_config()
        self.sock = None

    def connect(self):
        """Establece conexión con el servidor"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)  # Evita bloqueos en la conexión
            self.sock.connect((self.config['server_host'], self.config['server_port']))
            print(f"{Fore.GREEN}✅ Conexión exitosa a {
                  self.config['server_host']}:{self.config['server_port']}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error de conexión: {str(e)}{Style.RESET_ALL}")
            return False

    def send_message(self, message):
        """Envía un mensaje al servidor y recibe la respuesta"""
        try:
            self.sock.sendall(message.encode('utf-8'))
            response = self.sock.recv(4096).decode('utf-8')  # Buffer grande para recibir datos completos
            return response
        except socket.timeout:
            print(f"{Fore.RED}⚠️ Tiempo de espera agotado al recibir la respuesta.{Style.RESET_ALL}")
            return ""
        except Exception as e:
            print(f"{Fore.RED}⚠️ Error en la comunicación: {str(e)}{Style.RESET_ALL}")
            return ""

    def interactive_session(self):
        """Modo interactivo para enviar mensajes al servidor"""
        print(f"\n{Fore.CYAN}💬 Cliente TCP Básico{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Escribe tus mensajes (o 'exit' para salir):{Style.RESET_ALL}")
        
        while True:
            try:
                message = input(f"{Fore.BLUE}>>> {Style.RESET_ALL}").strip()
                
                if message.lower() == 'exit':
                    print(f"{Fore.YELLOW}👋 Cerrando conexión...{Style.RESET_ALL}")
                    break
                
                response = self.send_message(message)
                if response:
                    print(f"{Fore.GREEN}📩 Respuesta: {response}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ No se recibió respuesta del servidor{Style.RESET_ALL}")
                    break

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️ Conexión interrumpida{Style.RESET_ALL}")
                break

    def close(self):
        """Cierra la conexión con el servidor"""
        if self.sock:
            self.sock.close()
            print(f"{Fore.YELLOW}🔌 Conexión cerrada{Style.RESET_ALL}")

if __name__ == "__main__":
    client = SimpleTCPClient()
    if client.connect():
        client.interactive_session()
    client.close()
