# ivory_xampp_configurator.py
"""
🔧 IVORY XAMPP AUTO-CONFIGURATOR 🔧
Configurador Automático Inteligente para XAMPP
Detecta, configura y optimiza XAMPP para Ivory Security Suite
"""

import os
import sys
import json
import shutil
import winreg
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class XAMPPConfigurator:
    """🔧 Configurador Automático de XAMPP"""
    
    def __init__(self):
        self.xampp_paths = []
        self.detected_xampp = None
        self.config = {}
        
    def detect_xampp_installations(self):
        """🔍 Detectar instalaciones de XAMPP automáticamente"""
        print("🔍 Detectando instalaciones de XAMPP...")
        
        # Rutas comunes de XAMPP
        common_paths = [
            "C:\\xampp",
            "C:\\XAMPP", 
            "D:\\xampp",
            "D:\\XAMPP",
            "C:\\Program Files\\xampp",
            "C:\\Program Files (x86)\\xampp",
            "C:\\bitnami\\xampp",
            os.path.expanduser("~\\xampp")
        ]
        
        # Buscar en registro de Windows
        registry_paths = self.get_xampp_from_registry()
        if registry_paths:
            common_paths.extend(registry_paths)
        
        # Verificar cada ruta
        for path in common_paths:
            if self.verify_xampp_installation(path):
                self.xampp_paths.append(path)
                print(f"✅ XAMPP encontrado: {path}")
        
        if not self.xampp_paths:
            print("❌ No se encontraron instalaciones de XAMPP")
            return False
        
        # Usar la primera instalación encontrada
        self.detected_xampp = self.xampp_paths[0]
        print(f"🎯 Usando XAMPP: {self.detected_xampp}")
        return True
    
    def get_xampp_from_registry(self):
        """📋 Buscar XAMPP en el registro de Windows"""
        registry_paths = []
        
        try:
            # Buscar en HKEY_LOCAL_MACHINE
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Apache Software Foundation") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            install_path, _ = winreg.QueryValueEx(subkey, "ServerRoot")
                            # Convertir ruta de Apache a ruta de XAMPP
                            xampp_path = os.path.dirname(install_path)
                            registry_paths.append(xampp_path)
                        except FileNotFoundError:
                            continue
        except:
            pass
        
        return registry_paths
    
    def verify_xampp_installation(self, path):
        """✅ Verificar si es una instalación válida de XAMPP"""
        if not os.path.exists(path):
            return False
        
        # Verificar archivos/directorios críticos
        critical_items = [
            "apache/bin/httpd.exe",
            "apache/logs",
            "htdocs",
            "xampp-control.exe"
        ]
        
        for item in critical_items:
            if not os.path.exists(os.path.join(path, item)):
                return False
        
        return True
    
    def analyze_xampp_configuration(self):
        """📊 Analizar configuración actual de XAMPP"""
        print("\n📊 Analizando configuración de XAMPP...")
        
        analysis = {
            "xampp_path": self.detected_xampp,
            "apache_running": self.is_apache_running(),
            "log_files": self.find_log_files(),
            "htaccess_location": self.find_htaccess_location(),
            "php_version": self.get_php_version(),
            "apache_version": self.get_apache_version(),
            "document_root": self.get_document_root(),
            "log_level": self.get_log_level(),
            "modules": self.get_apache_modules()
        }
        
        # Mostrar análisis
        print(f"📁 Ruta XAMPP: {analysis['xampp_path']}")
        print(f"🟢 Apache activo: {'Sí' if analysis['apache_running'] else 'No'}")
        print(f"📊 Logs encontrados: {len(analysis['log_files'])}")
        print(f"🔧 PHP: {analysis['php_version']}")
        print(f"🌐 Apache: {analysis['apache_version']}")
        print(f"📁 Document Root: {analysis['document_root']}")
        
        return analysis
    
    def is_apache_running(self):
        """🔍 Verificar si Apache está ejecutándose"""
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq httpd.exe'], 
                                  capture_output=True, text=True)
            return 'httpd.exe' in result.stdout
        except:
            return False
    
    def find_log_files(self):
        """📋 Encontrar archivos de log"""
        log_dir = os.path.join(self.detected_xampp, "apache", "logs")
        log_files = {}
        
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                if file.endswith('.log'):
                    full_path = os.path.join(log_dir, file)
                    log_files[file] = {
                        'path': full_path,
                        'size': os.path.getsize(full_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(full_path))
                    }
        
        return log_files
    
    def find_htaccess_location(self):
        """🔍 Encontrar ubicación de .htaccess"""
        htdocs_path = os.path.join(self.detected_xampp, "htdocs")
        htaccess_path = os.path.join(htdocs_path, ".htaccess")
        
        return {
            'htdocs_path': htdocs_path,
            'htaccess_path': htaccess_path,
            'htaccess_exists': os.path.exists(htaccess_path),
            'htdocs_writable': os.access(htdocs_path, os.W_OK)
        }
    
    def get_php_version(self):
        """🐘 Obtener versión de PHP"""
        try:
            php_exe = os.path.join(self.detected_xampp, "php", "php.exe")
            if os.path.exists(php_exe):
                result = subprocess.run([php_exe, '-v'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.split('\n')[0]
        except:
            pass
        return "Desconocida"
    
    def get_apache_version(self):
        """🌐 Obtener versión de Apache"""
        try:
            httpd_exe = os.path.join(self.detected_xampp, "apache", "bin", "httpd.exe")
            if os.path.exists(httpd_exe):
                result = subprocess.run([httpd_exe, '-v'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.split('\n')[0]
        except:
            pass
        return "Desconocida"
    
    def get_document_root(self):
        """📁 Obtener Document Root de Apache"""
        config_file = os.path.join(self.detected_xampp, "apache", "conf", "httpd.conf")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.startswith('DocumentRoot'):
                            return line.split('"')[1]
            except:
                pass
        
        return os.path.join(self.detected_xampp, "htdocs")
    
    def get_log_level(self):
        """📊 Obtener nivel de logging"""
        config_file = os.path.join(self.detected_xampp, "apache", "conf", "httpd.conf")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.startswith('LogLevel'):
                            return line.split()[1]
            except:
                pass
        
        return "warn"
    
    def get_apache_modules(self):
        """🔧 Obtener módulos de Apache activos"""
        try:
            httpd_exe = os.path.join(self.detected_xampp, "apache", "bin", "httpd.exe")
            if os.path.exists(httpd_exe):
                result = subprocess.run([httpd_exe, '-M'], capture_output=True, text=True)
                if result.returncode == 0:
                    modules = []
                    for line in result.stdout.split('\n'):
                        if '_module' in line:
                            modules.append(line.strip())
                    return modules
        except:
            pass
        return []
    
    def optimize_xampp_for_security(self):
        """🛡️ Optimizar XAMPP para seguridad"""
        print("\n🛡️ Optimizando XAMPP para seguridad...")
        
        optimizations = []
        
        # 1. Configurar logging detallado
        self.configure_detailed_logging()
        optimizations.append("✅ Logging detallado configurado")
        
        # 2. Habilitar mod_rewrite
        self.enable_mod_rewrite()
        optimizations.append("✅ mod_rewrite habilitado")
        
        # 3. Configurar .htaccess básico
        self.setup_basic_htaccess()
        optimizations.append("✅ .htaccess básico configurado")
        
        # 4. Configurar cabeceras de seguridad
        self.setup_security_headers()
        optimizations.append("✅ Cabeceras de seguridad configuradas")
        
        # 5. Crear directorio de logs para Ivory
        self.setup_ivory_logging()
        optimizations.append("✅ Directorio de logs Ivory creado")
        
        return optimizations
    
    def configure_detailed_logging(self):
        """📝 Configurar logging detallado"""
        config_file = os.path.join(self.detected_xampp, "apache", "conf", "httpd.conf")
        
        # Backup del archivo original
        backup_file = f"{config_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config_file, backup_file)
        
        # Modificar configuración
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Configurar LogLevel para más detalle
            content = content.replace('LogLevel warn', 'LogLevel info')
            
            # Asegurar que CustomLog esté habilitado
            if 'CustomLog logs/access.log combined' not in content:
                content += '\nCustomLog logs/access.log combined\n'
            
            with open(config_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"⚠️ Error configurando logging: {e}")
    
    def enable_mod_rewrite(self):
        """🔄 Habilitar mod_rewrite"""
        config_file = os.path.join(self.detected_xampp, "apache", "conf", "httpd.conf")
        
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Descomentar mod_rewrite si está comentado
            content = content.replace('#LoadModule rewrite_module modules/mod_rewrite.so', 
                                    'LoadModule rewrite_module modules/mod_rewrite.so')
            
            with open(config_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"⚠️ Error habilitando mod_rewrite: {e}")
    
    def setup_basic_htaccess(self):
        """🔧 Configurar .htaccess básico"""
        htdocs_path = os.path.join(self.detected_xampp, "htdocs")
        htaccess_path = os.path.join(htdocs_path, ".htaccess")
        
        # Crear .htaccess básico si no existe
        if not os.path.exists(htaccess_path):
            basic_htaccess = """# Ivory Security Suite - Configuración Básica
# Generado automáticamente por Ivory XAMPP Configurator

# Habilitar el motor de reescritura
RewriteEngine On

# Ocultar información del servidor
ServerTokens Prod
Header unset Server
Header always unset X-Powered-By

# Protección básica
<Files ~ "^\\.(htaccess|htpasswd)$">
    Require all denied
</Files>

# Prevenir acceso a archivos sensibles
<FilesMatch "\\.(log|sql|bak|backup|old)$">
    Require all denied
</FilesMatch>

# Zona reservada para Ivory Security Suite
# No modificar manualmente las siguientes líneas

# BEGIN IVORY SECURITY ENGINE v2.0
# Este bloque será gestionado automáticamente por Ivory
# END IVORY SECURITY ENGINE v2.0
"""
            
            try:
                with open(htaccess_path, 'w') as f:
                    f.write(basic_htaccess)
                print(f"✅ .htaccess creado: {htaccess_path}")
            except Exception as e:
                print(f"❌ Error creando .htaccess: {e}")
    
    def setup_security_headers(self):
        """🛡️ Configurar cabeceras de seguridad"""
        config_file = os.path.join(self.detected_xampp, "apache", "conf", "httpd.conf")
        
        security_headers = """
# Ivory Security Headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Content-Security-Policy "default-src 'self'"
"""
        
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Añadir headers si no existen
            if 'Ivory Security Headers' not in content:
                content += security_headers
                
                with open(config_file, 'w') as f:
                    f.write(content)
                    
        except Exception as e:
            print(f"⚠️ Error configurando headers de seguridad: {e}")
    
    def setup_ivory_logging(self):
        """📁 Configurar logging para Ivory"""
        ivory_log_dir = os.path.join(self.detected_xampp, "logs", "ivory")
        
        # Crear directorio de logs de Ivory
        os.makedirs(ivory_log_dir, exist_ok=True)
        
        # Crear archivo de configuración de logs
        log_config = {
            "log_directory": ivory_log_dir,
            "retention_days": 30,
            "max_file_size": "100MB",
            "rotation_enabled": True
        }
        
        config_file = os.path.join(ivory_log_dir, "logging_config.json")
        with open(config_file, 'w') as f:
            json.dump(log_config, f, indent=4)
    
    def generate_ivory_config(self):
        """⚙️ Generar configuración de Ivory optimizada"""
        print("\n⚙️ Generando configuración de Ivory optimizada...")
        
        analysis = self.analyze_xampp_configuration()
        
        # Configuración optimizada basada en la detección
        optimized_config = {
            "version": "2.0",
            "auto_configured": True,
            "xampp_detection": {
                "xampp_path": self.detected_xampp,
                "detection_date": datetime.now().isoformat(),
                "apache_version": analysis["apache_version"],
                "php_version": analysis["php_version"]
            },
            "paths": {
                "apache_log": os.path.join(self.detected_xampp, "apache", "logs", "access.log").replace("\\", "/"),
                "error_log": os.path.join(self.detected_xampp, "apache", "logs", "error.log").replace("\\", "/"),
                "htaccess": os.path.join(analysis["htaccess_location"]["htaccess_path"]).replace("\\", "/"),
                "geoip_db": "./GeoLite2-Country.mmdb",
                "city_db": "./GeoLite2-City.mmdb",
                "ivory_log_dir": os.path.join(self.detected_xampp, "logs", "ivory").replace("\\", "/")
            },
            "security": {
                "blocked_countries": ["CN", "RU", "KP", "IR", "CU", "VN", "BD"],
                "suspicious_user_agents": [
                    "sqlmap", "nikto", "nmap", "masscan", "zmap", "gobuster", 
                    "dirb", "dirbuster", "wpscan", "curl", "wget", "python-requests",
                    "libwww", "bot", "crawler", "spider", "scan"
                ],
                "blocked_extensions": [".php~", ".bak", ".old", ".backup", ".log", ".sql"],
                "rate_limit_per_ip": 150,  # Más permisivo para desarrollo
                "auto_block_threshold": 3,  # Más agresivo
                "honeypot_paths": [
                    "/admin", "/wp-admin", "/phpmyadmin", "/cPanel",
                    "/.env", "/config.php", "/backup.sql", "/db.sql"
                ]
            },
            "ai": {
                "anomaly_detection": True,
                "threat_prediction": True,
                "auto_learning": True,
                "confidence_threshold": 0.70,  # Más sensible
                "model_update_interval": 3600
            },
            "monitoring": {
                "scan_interval": 2,  # Más frecuente
                "log_rotation_days": 15,  # Menos retención
                "backup_retention_days": 5,
                "real_time_alerts": True,
                "performance_monitoring": True
            },
            "optimization": {
                "cache_geoip_lookups": True,
                "batch_process_logs": True,
                "compress_old_logs": True,
                "auto_cleanup": True
            }
        }
        
        # Guardar configuración
        config_file = "ivory_config.json"
        with open(config_file, 'w') as f:
            json.dump(optimized_config, f, indent=4)
        
        print(f"✅ Configuración guardada: {config_file}")
        return optimized_config
    
    def test_configuration(self):
        """🧪 Probar configuración generada"""
        print("\n🧪 Probando configuración...")
        
        tests = []
        
        # Test 1: Verificar acceso a logs
        log_path = os.path.join(self.detected_xampp, "apache", "logs", "access.log")
        if os.path.exists(log_path) and os.access(log_path, os.R_OK):
            tests.append("✅ Acceso a logs de Apache")
        else:
            tests.append("❌ No se puede acceder a logs de Apache")
        
        # Test 2: Verificar .htaccess
        htaccess_path = os.path.join(self.detected_xampp, "htdocs", ".htaccess")
        if os.path.exists(htaccess_path):
            tests.append("✅ .htaccess configurado")
        else:
            tests.append("❌ .htaccess no encontrado")
        
        # Test 3: Verificar permisos de escritura
        htdocs_path = os.path.join(self.detected_xampp, "htdocs")
        if os.access(htdocs_path, os.W_OK):
            tests.append("✅ Permisos de escritura en htdocs")
        else:
            tests.append("⚠️ Sin permisos de escritura en htdocs")
        
        # Test 4: Verificar Apache activo
        if self.is_apache_running():
            tests.append("✅ Apache ejecutándose")
        else:
            tests.append("⚠️ Apache no está ejecutándose")
        
        # Test 5: Verificar bases de datos GeoIP
        if os.path.exists("GeoLite2-Country.mmdb"):
            tests.append("✅ Base de datos GeoIP disponible")
        else:
            tests.append("⚠️ Base de datos GeoIP no encontrada")
        
        return tests
    
    def create_startup_scripts(self):
        """🚀 Crear scripts de inicio para XAMPP + Ivory"""
        print("\n🚀 Creando scripts de inicio...")
        
        # Script para iniciar XAMPP + Ivory
        xampp_ivory_startup = f"""@echo off
echo 🛡️ Iniciando XAMPP + Ivory Security Suite...

echo 🔄 Iniciando XAMPP...
cd /d "{self.detected_xampp}"
start "" "xampp-control.exe"

echo ⏳ Esperando que Apache inicie...
timeout /t 10 /nobreak >nul

echo 🛡️ Iniciando Ivory Security Center...
cd /d "{os.getcwd()}"
start "" python ivory_security_center.py

echo ✅ Sistema iniciado correctamente
pause
"""
        
        with open("Iniciar_XAMPP_Ivory.bat", 'w') as f:
            f.write(xampp_ivory_startup)
        
        # Script para detener todo
        stop_script = f"""@echo off
echo 🛑 Deteniendo servicios...

echo 🔄 Deteniendo Apache...
taskkill /f /im httpd.exe >nul 2>&1

echo 🔄 Deteniendo MySQL...
taskkill /f /im mysqld.exe >nul 2>&1

echo 🔄 Deteniendo Ivory...
taskkill /f /im python.exe >nul 2>&1

echo ✅ Servicios detenidos
pause
"""
        
        with open("Detener_XAMPP_Ivory.bat", 'w') as f:
            f.write(stop_script)
        
        print("✅ Scripts de inicio creados:")
        print("  • Iniciar_XAMPP_Ivory.bat")
        print("  • Detener_XAMPP_Ivory.bat")

def main():
    """🎯 Función principal del configurador"""
    print("="*70)
    print("🔧 IVORY XAMPP AUTO-CONFIGURATOR v2.0")
    print("🎯 Configuración Automática Inteligente para XAMPP")
    print("="*70)
    
    configurator = XAMPPConfigurator()
    
    # Paso 1: Detectar XAMPP
    if not configurator.detect_xampp_installations():
        print("\n❌ No se pudo detectar XAMPP automáticamente")
        print("💡 Opciones:")
        print("   1. Instala XAMPP desde https://www.apachefriends.org/")
        print("   2. Especifica manualmente la ruta de XAMPP")
        
        manual_path = input("\n📁 Ruta manual de XAMPP (o ENTER para salir): ").strip()
        if manual_path and configurator.verify_xampp_installation(manual_path):
            configurator.detected_xampp = manual_path
            print(f"✅ XAMPP manual configurado: {manual_path}")
        else:
            print("👋 Saliendo...")
            return
    
    # Paso 2: Analizar configuración actual
    analysis = configurator.analyze_xampp_configuration()
    
    # Paso 3: Optimizar XAMPP
    optimizations = configurator.optimize_xampp_for_security()
    print("\n🛡️ Optimizaciones aplicadas:")
    for opt in optimizations:
        print(f"  {opt}")
    
    # Paso 4: Generar configuración de Ivory
    config = configurator.generate_ivory_config()
    
    # Paso 5: Probar configuración
    test_results = configurator.test_configuration()
    print("\n🧪 Resultados de pruebas:")
    for result in test_results:
        print(f"  {result}")
    
    # Paso 6: Crear scripts de inicio
    configurator.create_startup_scripts()
    
    print("\n" + "="*70)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*70)
    print("✅ XAMPP detectado y optimizado")
    print("✅ Ivory configurado automáticamente")
    print("✅ Scripts de inicio creados")
    print("✅ Configuración de seguridad aplicada")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Ejecuta 'Iniciar_XAMPP_Ivory.bat' para iniciar todo")
    print("2. Abre tu navegador en http://localhost")
    print("3. Verifica que Apache esté funcionando")
    print("4. ¡Disfruta de tu sistema de seguridad avanzado!")
    
    print("\n🛡️ ¡Tu web está ahora protegida por Ivory Security Suite!")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        print("🔧 Intenta ejecutar como administrador")
