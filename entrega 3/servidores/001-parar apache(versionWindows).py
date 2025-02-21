# apache_manager_win.py
import subprocess
import sys
import logging
from typing import Tuple, Optional

# Configuración de logging
logging.basicConfig(
    filename='apache_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SERVICIO_APACHE = "Apache2.4"  # Nombre exacto del servicio en Windows

def ejecutar_comando_powershell(comando: str) -> Tuple[bool, str]:
    """
    Ejecuta un comando de PowerShell con privilegios elevados
    
    Args:
        comando: Comando PowerShell a ejecutar
        
    Returns:
        Tuple (éxito, mensaje)
    """
    try:
        resultado = subprocess.run(
            ["powershell", "-Command", comando],
            check=True,
            text=True,
            capture_output=True,
            timeout=15,
            shell=True
        )
        return True, resultado.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Error {e.returncode}: {e.stderr.strip()}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def verificar_estado_servicio() -> bool:
    """
    Verifica si el servicio Apache está en ejecución
    """
    comando = f"Get-Service -Name '{SERVICIO_APACHE}' | Select-Object Status"
    exito, salida = ejecutar_comando_powershell(comando)
    
    return exito and "Running" in salida

def detener_apache() -> bool:
    """
    Detiene el servicio Apache en Windows con verificaciones
    """
    try:
        # Verificar si el servicio existe
        comando_check = f"Get-Service -Name '{SERVICIO_APACHE}' -ErrorAction Stop"
        if not ejecutar_comando_powershell(comando_check)[0]:
            logging.error("Servicio Apache no encontrado")
            print("❌ Servicio Apache no instalado o nombre incorrecto")
            return False
            
        # Verificar estado actual
        if not verificar_estado_servicio():
            logging.warning("Apache ya está detenido")
            print("⚠️ Apache ya se encuentra detenido")
            return True
            
        # Detener servicio
        logging.info("Deteniendo Apache...")
        comando_stop = f"Stop-Service -Name '{SERVICIO_APACHE}' -Force"
        exito, mensaje = ejecutar_comando_powershell(comando_stop)
        
        if exito:
            logging.info("Apache detenido exitosamente")
            
            # Verificación adicional
            if verificar_estado_servicio():
                logging.error("Apache sigue activo después de detener")
                print("❌ El servicio no se detuvo completamente")
                return False
                
            print("✅ Apache detenido correctamente")
            return True
            
        logging.error(f"Fallo al detener Apache: {mensaje}")
        print(f"❌ Error: {mensaje}")
        return False
        
    except Exception as e:
        logging.critical(f"Error crítico: {str(e)}", exc_info=True)
        print(f"🚨 Error crítico: {str(e)}")
        return False

def verificar_requisitos() -> Optional[str]:
    """Verifica requisitos del sistema"""
    try:
        # Verificar si PowerShell está disponible
        subprocess.run(["powershell", "-Command", "exit 0"], check=True, timeout=5)
        
        # Verificar si el servicio existe
        if not ejecutar_comando_powershell(f"Get-Service -Name '{SERVICIO_APACHE}' -ErrorAction SilentlyContinue")[0]:
            return f"El servicio '{SERVICIO_APACHE}' no está instalado"
            
    except Exception as e:
        return f"Error en verificaciones: {str(e)}"
    
    return None

def main():
    print("\nGestión de Apache en Windows")
    print("=" * 30)
    
    # Verificar requisitos
    if error := verificar_requisitos():
        print(f"\n❌ Pre-requisitos fallidos: {error}")
        print(f"Verifique que el servicio '{SERVICIO_APACHE}' esté instalado")
        sys.exit(1)
        
    # Intentar detener Apache
    if detener_apache():
        print("\nOperación completada exitosamente")
        sys.exit(0)
    else:
        print("\nNo se pudo completar la operación")
        sys.exit(2)

if __name__ == "__main__":
    # Requiere ejecución como administrador
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        sys.exit(3)