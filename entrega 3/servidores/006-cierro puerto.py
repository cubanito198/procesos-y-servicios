"""
Script para bloquear puertos específicos utilizando iptables.
"""

import subprocess
from typing import Optional

def block_port(port: str, ip: Optional[str] = None) -> bool:
    """
    Bloquea un puerto específico mediante iptables.
    
    Args:
        port (str): Número del puerto a bloquear.
        ip (Optional[str]): Dirección IP a bloquear (opcional).
    
    Returns:
        bool: True si la operación fue exitosa, False en caso de error.
    """
    if not port.isdigit():
        print("❌ Número de puerto no válido. Debe ser un número.")
        return False
    
    command = ["sudo", "iptables", "-A", "INPUT", "-p", "tcp", "--dport", port, "-j", "DROP"]
    if ip:
        command.insert(-2, "-s")
        command.insert(-2, ip)
    
    try:
        subprocess.run(command, check=True)
        print(f"✅ Puerto {port} bloqueado {'para la IP ' + ip if ip else 'para todas las IPs'}.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error: No se pudo bloquear el puerto. Asegúrate de tener privilegios de sudo.")
        return False

def main():
    """Solicita al usuario un puerto y una IP opcional para bloquear."""
    port = input("🔢 Introduce el puerto que deseas bloquear: ").strip()
    ip = input("🌍 Introduce la IP a bloquear (dejar en blanco para todas): ").strip() or None
    block_port(port, ip)

if __name__ == "__main__":
    main()
