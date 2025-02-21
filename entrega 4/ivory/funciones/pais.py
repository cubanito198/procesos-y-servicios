# funciones/pais.py
import geoip2.database
import ipaddress
import os
import re
import shutil
from datetime import datetime

# Configuración directa en el código
RUTA_LOG = r'C:\xampp\apache\logs\access.log'
RUTA_HTACCESS = r'C:\xampp\htdocs\.htaccess'
RUTA_GEOLITE = 'GeoLite2-Country.mmdb'
PAISES_BLOQUEADOS = {'Spain', 'cuba', 'Ukraine'}  # Editar directamente aquí

def validar_ip(ip: str) -> bool:
    """Valida una dirección IPv4/IPv6"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def obtener_pais(ip: str, lector) -> str:
    """Obtiene el país desde la base de datos GeoIP"""
    try:
        return lector.country(ip).country.name
    except Exception:
        return 'Desconocido'

def actualizar_htaccess(ips_bloqueadas: set):
    """Actualiza el .htaccess con las nuevas reglas"""
    marcador_inicio = "# BEGIN Bloqueo por País"
    marcador_fin = "# END Bloqueo por País"
    
    try:
        # Crear backup
        backup_path = f"{RUTA_HTACCESS}.backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if os.path.exists(RUTA_HTACCESS):
            shutil.copy2(RUTA_HTACCESS, backup_path)
        
        # Leer contenido existente
        lineas = []
        if os.path.exists(RUTA_HTACCESS):
            with open(RUTA_HTACCESS, 'r') as f:
                lineas = f.readlines()
        
        # Filtrar bloque existente
        nuevo_contenido = []
        en_bloque = False
        ips_existentes = set()
        
        for linea in lineas:
            if marcador_inicio in linea:
                en_bloque = True
            if marcador_fin in linea:
                en_bloque = False
            if not en_bloque:
                nuevo_contenido.append(linea)
            else:
                if "Require not ip" in linea:
                    ip = linea.split()[-1].strip()
                    ips_existentes.add(ip)
        
        # Añadir nuevas IPs
        nuevas_ips = sorted(ips_bloqueadas - ips_existentes)
        if nuevas_ips:
            nuevo_contenido += [
                f"\n{marcador_inicio}\n",
                "<RequireAll>\n",
                "    Require all granted\n"
            ]
            nuevo_contenido += [f"    Require not ip {ip}\n" for ip in nuevas_ips]
            nuevo_contenido += [f"{marcador_fin}\n"]
            
            # Escribir archivo
            with open(RUTA_HTACCESS, 'w') as f:
                f.writelines(nuevo_contenido)
            
            print(f"✔ {len(nuevas_ips)} IPs bloqueadas exitosamente")
            print(f"Backup guardado en: {backup_path}")
        else:
            print("No hay nuevas IPs para bloquear")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'backup_path' in locals() and os.path.exists(backup_path):
            print("Restaurando backup...")
            shutil.copy2(backup_path, RUTA_HTACCESS)

def procesar_logs():
    """Procesa el archivo de logs de Apache"""
    if not os.path.exists(RUTA_LOG):
        print(f"❌ Archivo de logs no encontrado: {RUTA_LOG}")
        return set()
    
    ips = set()
    patron_ip = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    
    try:
        with open(RUTA_LOG, 'r') as f:
            for linea in f:
                ip = patron_ip.search(linea)
                if ip and validar_ip(ip.group()):
                    ips.add(ip.group())
    except Exception as e:
        print(f"❌ Error leyendo logs: {str(e)}")
    
    return ips

def main():
    # Verificar existencia de GeoIP
    if not os.path.exists(RUTA_GEOLITE):
        print(f"❌ Base de datos GeoIP no encontrada: {RUTA_GEOLITE}")
        return
    
    # Procesar IPs
    ips = procesar_logs()
    if not ips:
        print("No se encontraron IPs válidas en los logs")
        return
    
    # Obtener países
    ips_bloqueadas = set()
    with geoip2.database.Reader(RUTA_GEOLITE) as lector:
        for ip in ips:
            if obtener_pais(ip, lector) in PAISES_BLOQUEADOS:
                ips_bloqueadas.add(ip)
    
    # Aplicar bloqueo
    if ips_bloqueadas:
        print("\n🚨 IPs a bloquear:")
        for ip in sorted(ips_bloqueadas):
            print(f" - {ip}")
        actualizar_htaccess(ips_bloqueadas)
    else:
        print("\n✅ No se encontraron IPs de países bloqueados")

if __name__ == "__main__":
    print("=== Ivory - Bloqueo por País ===")
    print(f"🗺️ Países bloqueados: {', '.join(PAISES_BLOQUEADOS)}")
    main()
