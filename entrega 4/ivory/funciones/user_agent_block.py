# funciones/user_agent_block.py
"""
Módulo para bloquear IPs basado en User Agents sospechosos en XAMPP (Windows)
"""

import ipaddress
import os
import re
from datetime import datetime
from typing import Set, List

# Configuración de rutas para XAMPP
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
CONFIG = {
    'LOG_PATH': r'C:\xampp\apache\logs\access.log',
    'HTACCESS_PATH': os.path.join(BASE_DIR, '.htaccess'),
    'USER_AGENTS': {"-", "", "curl", "wget", "sqlmap", "nikto", "nmap"}
}

MARCADOR_INICIO = "# BEGIN Blocked IPs by User Agent"
MARCADOR_FIN = "# END Blocked IPs by User Agent"

def validar_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except ValueError:
        return False

def bloquear_ips_htaccess(ips_bloqueadas: Set[str]) -> None:
    """Actualiza .htaccess en el directorio padre"""
    try:
        htaccess_path = CONFIG['HTACCESS_PATH']
        backup_path = f"{htaccess_path}.backup_ua_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Crear backup
        if os.path.exists(htaccess_path):
            with open(htaccess_path, 'r') as orig, open(backup_path, 'w') as backup:
                backup.write(orig.read())
        
        # Procesar contenido
        lineas = []
        if os.path.exists(htaccess_path):
            with open(htaccess_path, 'r') as f:
                lineas = f.readlines()
        
        nuevo_contenido = []
        en_bloque = False
        ips_existentes = set()
        
        for linea in lineas:
            if MARCADOR_INICIO in linea:
                en_bloque = True
            if MARCADOR_FIN in linea:
                en_bloque = False
            if not en_bloque:
                nuevo_contenido.append(linea)
            else:
                if "Require not ip" in linea:
                    ip = linea.split("Require not ip")[1].strip()
                    ips_existentes.add(ip)
        
        # Generar nuevo bloque
        nuevas_ips = [ip for ip in ips_bloqueadas if ip not in ips_existentes]
        if nuevas_ips:
            nuevo_contenido.extend([
                f"\n{MARCADOR_INICIO}\n",
                "<RequireAll>\n",
                "    Require all granted\n"
            ])
            nuevo_contenido.extend(f"    Require not ip {ip}\n" for ip in sorted(nuevas_ips))
            nuevo_contenido.append(f"{MARCADOR_FIN}\n")
            
            # Escribir archivo
            with open(htaccess_path, 'w') as f:
                f.writelines(nuevo_contenido)
            
            print(f"✔ {len(nuevas_ips)} IPs bloqueadas en:\n{htaccess_path}")
            print(f"Backup guardado en:\n{backup_path}")
        else:
            print("No hay nuevas IPs para bloquear")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'backup_path' in locals() and os.path.exists(backup_path):
            print("↻ Restaurando backup...")
            os.replace(backup_path, htaccess_path)

def procesar_logs() -> Set[str]:
    """Procesa logs de XAMPP"""
    patron = re.compile(
        r'^(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?"(?P<user_agent>.*?)"$'
    )
    
    ips = set()
    
    try:
        with open(CONFIG['LOG_PATH'], 'r') as f:
            for linea in f:
                match = patron.search(linea)
                if match:
                    user_agent = match.group('user_agent').lower().strip()
                    if user_agent in CONFIG['USER_AGENTS']:
                        ip = match.group('ip')
                        if validar_ip(ip):
                            ips.add(ip)
    except Exception as e:
        print(f"❌ Error leyendo logs: {str(e)}")
    
    return ips

def generar_reporte(ips: List[str]) -> None:
    """Genera reporte en el directorio de logs"""
    if ips:
        reporte_path = os.path.join(
            os.path.dirname(CONFIG['LOG_PATH']),
            f"reporte_bloqueos_ua_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        
        try:
            with open(reporte_path, 'w') as f:
                f.write("IPs bloqueadas por User Agent Sospechoso\n")
                f.write("========================================\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("\n".join(sorted(ips)))
            
            print(f"📄 Reporte generado en:\n{reporte_path}")
        except Exception as e:
            print(f"⚠️ Error creando reporte: {str(e)}")

def main():
    print("=== Ivory - Bloqueo por User Agent ===")
    print(f"🔍 Analizando logs en:\n{CONFIG['LOG_PATH']}")
    
    ips = procesar_logs()
    
    if ips:
        print("\n🚨 IPs sospechosas detectadas:")
        for ip in sorted(ips):
            print(f" - {ip}")
        
        generar_reporte(sorted(ips))
        bloquear_ips_htaccess(ips)
    else:
        print("\n✅ No se encontraron IPs sospechosas")

if __name__ == "__main__":
    main()