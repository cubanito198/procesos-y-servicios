#!/usr/bin/env python3
"""
Escáner de puertos abiertos en el sistema local

Este script lista todos los puertos abiertos en el equipo mediante la biblioteca psutil.
"""

import psutil
import logging
from typing import List, Tuple

# Configuración del logging
logging.basicConfig(
    filename='open_ports.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def get_open_ports() -> List[Tuple[str, int]]:
    """Obtiene una lista de los puertos abiertos en el sistema."""
    open_ports = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN':
                ip = conn.laddr.ip if conn.laddr.ip else '0.0.0.0'
                open_ports.append((ip, conn.laddr.port))
        logging.info(f"Se encontraron {len(open_ports)} puertos abiertos.")
    except Exception as e:
        logging.error(f"Error al obtener puertos abiertos: {str(e)}")
    return open_ports

def mostrar_puertos():
    """Muestra los puertos abiertos en un formato claro."""
    ports = get_open_ports()
    if not ports:
        print("🔴 No se encontraron puertos abiertos.")
        return
    
    print("\n🔵 Puertos abiertos en el sistema:")
    print("=" * 30)
    for ip, port in ports:
        print(f"🌐 {ip}:{port}")
    print("=" * 30)

if __name__ == "__main__":
    mostrar_puertos()
