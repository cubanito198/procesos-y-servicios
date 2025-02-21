# ivory.py
"""
Ivory - Sistema de Bloqueo de IPs Avanzado
"""

import argparse
import logging
from datetime import datetime
from funciones.pais import main as country_block_main
from funciones.user_agent_block import main as user_agent_block_main
from colorama import Fore, Style, init

# Inicializar colores para la terminal
init(autoreset=True)

# Configuración centralizada
CONFIG = {
    'LOG_FILE': 'ivory.log',
    'MAX_BACKUPS': 5,
    'COLORES': {
        'exito': Fore.GREEN,
        'error': Fore.RED,
        'advertencia': Fore.YELLOW,
        'info': Fore.CYAN
    }
}

def configurar_logging():
    """Configura el sistema de logging unificado"""
    logging.basicConfig(
        filename=CONFIG['LOG_FILE'],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def mostrar_estado(mensaje, tipo='info'):
    """Muestra mensajes formateados con colores"""
    color = CONFIG['COLORES'].get(tipo, Fore.WHITE)
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] {mensaje}{Style.RESET_ALL}")

def gestionar_backups():
    """Elimina backups antiguos manteniendo solo los N más recientes"""
    try:
        backups = sorted([f for f in os.listdir() if '.backup' in f], 
                       key=os.path.getmtime, 
                       reverse=True)
        
        for old_backup in backups[CONFIG['MAX_BACKUPS']:]:
            os.remove(old_backup)
            logging.info(f"Backup eliminado: {old_backup}")
            
    except Exception as e:
        logging.error(f"Error gestionando backups: {str(e)}")

def ejecutar_proceso(funcion, nombre_proceso, args):
    """Ejecuta un proceso con manejo de errores unificado"""
    try:
        mostrar_estado(f"Iniciando {nombre_proceso}...", 'info')
        funcion()
        mostrar_estado(f"{nombre_proceso} completado", 'exito')
        return True
    except Exception as e:
        logging.error(f"Error en {nombre_proceso}: {str(e)}")
        mostrar_estado(f"Error en {nombre_proceso}: {str(e)}", 'error')
        return False
    finally:
        gestionar_backups()

def main():
    """Función principal con gestión de argumentos CLI"""
    parser = argparse.ArgumentParser(
        description='Ivory - Sistema de Bloqueo de IPs Avanzado',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--paises', action='store_true',
                      help='Ejecutar bloqueo por país')
    parser.add_argument('--user-agent', action='store_true',
                      help='Ejecutar bloqueo por User Agent')
    parser.add_argument('--dry-run', action='store_true',
                      help='Simular ejecución sin modificar archivos')
    parser.add_argument('--verbose', action='store_true',
                      help='Mostrar detalles de la ejecución')

    args = parser.parse_args()

    configurar_logging()
    logging.info("Inicio de ejecución de Ivory")

    # Nuevas funcionalidades: Control de procesos y modo dry-run
    resultados = []
    
    if args.dry_run:
        mostrar_estado("MODO SIMULACIÓN ACTIVADO - No se modificará ningún archivo", 'advertencia')

    if args.paises:
        resultados.append(
            ejecutar_proceso(
                lambda: country_block_main(dry_run=args.dry_run),
                "Bloqueo por país",
                args
            )
        )

    if args.user_agent:
        resultados.append(
            ejecutar_proceso(
                lambda: user_agent_block_main(dry_run=args.dry_run),
                "Bloqueo por User Agent",
                args
            )
        )

    # Mostrar resumen final
    if all(resultados):
        mostrar_estado("Proceso completado exitosamente", 'exito')
    else:
        mostrar_estado("Proceso completado con errores", 'error')

    logging.info("Fin de ejecución de Ivory\n")

if __name__ == "__main__":
    import os
    import sys
    try:
        main()
    except KeyboardInterrupt:
        print("\nEjecución cancelada por el usuario")
        sys.exit(1)

        # argumentos avanzados: 
        # python ivory.py --paises --user-agent  # Ejecutar ambos bloqueos
        # python ivory.py --paises --dry-run     # Simular solo bloqueo por país
        # python ivory.py --user-agent --verbose # Bloqueo UA con detalles
        
        # ejecucion recomendada python ivory.py --paises --user-agent --verbose