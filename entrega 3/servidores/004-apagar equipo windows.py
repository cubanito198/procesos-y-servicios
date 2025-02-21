#!/usr/bin/env python3
"""
Script avanzado para gestión de energía en Windows con múltiples opciones
"""

import subprocess
import sys
import logging
import ctypes
import time
from typing import Tuple, Optional

# Configuración de logging
logging.basicConfig(
    filename='gestor_energia.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def verificar_privilegios() -> bool:
    """Verifica si el programa se ejecuta con privilegios de administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logging.error(f"Error verificando privilegios: {str(e)}")
        return False

def ejecutar_comando(comando: list, tiempo_espera: int = 10) -> Tuple[bool, str]:
    """
    Ejecuta un comando del sistema con manejo seguro de errores
    
    Args:
        comando: Lista con el comando y argumentos
        tiempo_espera: Tiempo máximo de espera en segundos
        
    Returns:
        Tuple (éxito, mensaje)
    """
    try:
        resultado = subprocess.run(
            comando,
            check=True,
            text=True,
            capture_output=True,
            timeout=tiempo_espera,
            shell=True
        )
        return True, resultado.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Error {e.returncode}: {e.stderr.strip()}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def operacion_energia(accion: str, tiempo: int = 0) -> bool:
    """
    Realiza operaciones de gestión de energía
    
    Args:
        accion: Tipo de operación (apagar, reiniciar, hibernar, cancelar)
        tiempo: Tiempo en segundos antes de ejecutar la acción
        
    Returns:
        bool: True si la operación fue exitosa
    """
    acciones_validas = {
        'apagar': '/s',
        'reiniciar': '/r',
        'hibernar': '/h',
        'cancelar': '/a'
    }
    
    if accion not in acciones_validas:
        logging.error(f"Acción no válida: {accion}")
        return False
    
    comando = ["shutdown", acciones_validas[accion]]
    
    if accion != 'cancelar' and accion != 'hibernar':
        comando.extend(["/t", str(tiempo)])
    
    if accion == 'hibernar':
        comando = ["shutdown", "/h"]
    
    logging.info(f"Iniciando {accion} (tiempo: {tiempo}s)")
    exito, mensaje = ejecutar_comando(comando)
    
    if exito:
        logging.info(f"Operación {accion} exitosa")
        print(f"✅ Operación completada: {accion.capitalize()}")
        return True
    
    logging.error(f"Fallo en {accion}: {mensaje}")
    print(f"❌ Error: {mensaje}")
    return False

def confirmar_accion(tiempo: int = 30) -> bool:
    """
    Muestra una cuenta regresiva para cancelar la acción
    
    Args:
        tiempo: Tiempo total en segundos
        
    Returns:
        bool: True si se confirma la acción
    """
    print(f"\n⏳ Tienes {tiempo} segundos para cancelar (Presiona Ctrl+C)")
    
    try:
        for i in range(tiempo, 0, -1):
            print(f"Tiempo restante: {i}s", end='\r')
            time.sleep(1)
        return True
    except KeyboardInterrupt:
        print("\n🚫 Operación cancelada por el usuario")
        return False

def main():
    # Verificar privilegios de administrador
    if not verificar_privilegios():
        print("\n🔒 Error: Se requieren privilegios de administrador")
        print("Ejecuta el script como administrador")
        sys.exit(1)
    
    # Menú interactivo
    print("\n🔌 Gestión de Energía de Windows")
    print("=" * 40)
    print("1. Apagar equipo")
    print("2. Reiniciar equipo")
    print("3. Hibernar equipo")
    print("4. Cancelar operación programada")
    print("5. Salir")
    
    opcion = input("\nSeleccione una opción (1-5): ")
    
    acciones = {
        '1': 'apagar',
        '2': 'reiniciar',
        '3': 'hibernar',
        '4': 'cancelar'
    }
    
    if opcion == '5':
        print("\n👋 Programa finalizado")
        sys.exit(0)
        
    if opcion not in acciones:
        print("\n❌ Opción no válida")
        sys.exit(2)
        
    accion = acciones[opcion]
    
    # Configurar tiempo si es necesario
    tiempo = 30
    if accion in ['apagar', 'reiniciar']:
        try:
            tiempo = int(input("Ingrese tiempo en segundos (0 para inmediato): "))
        except ValueError:
            print("\n❌ Valor de tiempo no válido")
            sys.exit(3)
    
    # Confirmación y ejecución
    if accion != 'cancelar':
        if not confirmar_accion(tiempo if tiempo > 30 else 30):
            sys.exit(0)
    
    if operacion_energia(accion, tiempo):
        sys.exit(0)
    else:
        sys.exit(4)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🚫 Operación cancelada por el usuario")
        sys.exit(5)