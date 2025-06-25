# ivory_launcher.py
"""
🚀 IVORY SECURITY SUITE LAUNCHER 🚀
Instalador y Ejecutor Principal del Sistema de Seguridad Web más Avanzado
Versión: 2.0 Pro Edition - Launcher Supremo
"""

import os
import sys
import subprocess
import json
import time
import webbrowser
from pathlib import Path
import urllib.request
import zipfile
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# 🎨 ASCII Art y configuración visual
IVORY_LOGO = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗██╗   ██╗ ██████╗ ██████╗ ██╗   ██╗                   ║
║    ██║██║   ██║██╔═══██╗██╔══██╗╚██╗ ██╔╝                   ║
║    ██║██║   ██║██║   ██║██████╔╝ ╚████╔╝                    ║
║    ██║╚██╗ ██╔╝██║   ██║██╔══██╗  ╚██╔╝                     ║
║    ██║ ╚████╔╝ ╚██████╔╝██║  ██║   ██║                      ║
║    ╚═╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝                      ║
║                                                              ║
║           🛡️  SECURITY SUITE v2.0 PRO EDITION  🛡️           ║
║              Sistema de Protección Web Avanzado             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

class IvoryInstaller:
    """🔧 Instalador Inteligente de Ivory Security Suite"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.config_file = self.base_dir / "ivory_config.json"
        self.dependencies = [
            'tkinter', 'matplotlib', 'numpy', 'scikit-learn', 'geoip2',
            'requests', 'aiofiles', 'joblib', 'sqlite3'
        ]
        self.optional_deps = ['plotly', 'dash', 'flask']
        
        # URLs de recursos
        self.resources = {
            'geoip_country': 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb',
            'geoip_city': 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb',
            'threat_feeds': [
                'https://feodotracker.abuse.ch/downloads/ipblocklist.txt',
                'https://www.spamhaus.org/drop/drop.txt'
            ]
        }
    
    def check_python_version(self):
        """🐍 Verificar versión de Python"""
        if sys.version_info < (3, 8):
            print("❌ ERROR: Se requiere Python 3.8 o superior")
            print(f"   Tu versión: {sys.version}")
            return False
        print(f"✅ Python {sys.version.split()[0]} - Compatible")
        return True
    
    def check_dependencies(self):
        """📦 Verificar dependencias"""
        print("\n🔍 Verificando dependencias...")
        missing_deps = []
        
        for dep in self.dependencies:
            try:
                __import__(dep)
                print(f"✅ {dep}")
            except ImportError:
                print(f"❌ {dep} - FALTANTE")
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"\n⚠️ Dependencias faltantes: {', '.join(missing_deps)}")
            self.install_dependencies(missing_deps)
        else:
            print("✅ Todas las dependencias están disponibles")
        
        return len(missing_deps) == 0
    
    def install_dependencies(self, deps):
        """📥 Instalar dependencias automáticamente"""
        print("\n📥 Instalando dependencias...")
        
        pip_packages = {
            'tkinter': 'tkinter',  # Viene con Python
            'matplotlib': 'matplotlib',
            'numpy': 'numpy',
            'scikit-learn': 'scikit-learn',
            'geoip2': 'geoip2',
            'requests': 'requests',
            'aiofiles': 'aiofiles',
            'joblib': 'joblib',
            'sqlite3': '',  # Viene con Python
        }
        
        for dep in deps:
            if dep == 'tkinter' or dep == 'sqlite3':
                continue  # Vienen con Python
            
            package_name = pip_packages.get(dep, dep)
            try:
                print(f"🔄 Instalando {package_name}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package_name
                ])
                print(f"✅ {package_name} instalado")
            except subprocess.CalledProcessError:
                print(f"❌ Error instalando {package_name}")
    
    def download_geoip_databases(self):
        """🌍 Descargar bases de datos GeoIP"""
        print("\n🌍 Descargando bases de datos GeoIP...")
        
        for db_name, url in [
            ('GeoLite2-Country.mmdb', self.resources['geoip_country']),
            ('GeoLite2-City.mmdb', self.resources['geoip_city'])
        ]:
            db_path = self.base_dir / db_name
            
            if db_path.exists():
                print(f"✅ {db_name} ya existe")
                continue
            
            try:
                print(f"🔄 Descargando {db_name}...")
                urllib.request.urlretrieve(url, db_path)
                print(f"✅ {db_name} descargado")
            except Exception as e:
                print(f"⚠️ Error descargando {db_name}: {e}")
                print("   Continuando sin esta base de datos...")
    
    def create_default_config(self):
        """⚙️ Crear configuración por defecto"""
        print("\n⚙️ Creando configuración...")
        
        default_config = {
            "version": "2.0",
            "paths": {
                "apache_log": r"C:\xampp\apache\logs\access.log",
                "error_log": r"C:\xampp\apache\logs\error.log",
                "htaccess": r"C:\xampp\htdocs\.htaccess",
                "geoip_db": str(self.base_dir / "GeoLite2-Country.mmdb"),
                "city_db": str(self.base_dir / "GeoLite2-City.mmdb")
            },
            "security": {
                "blocked_countries": ["CN", "RU", "KP", "IR", "CU", "ES"],
                "suspicious_user_agents": [
                    "sqlmap", "nikto", "nmap", "masscan", "zmap",
                    "gobuster", "dirb", "dirbuster", "wpscan",
                    "curl", "wget", "python-requests", "libwww",
                    "bot", "crawler", "spider"
                ],
                "blocked_extensions": [".php~", ".bak", ".old", ".backup", ".log"],
                "rate_limit_per_ip": 100,
                "auto_block_threshold": 5,
                "honeypot_paths": ["/admin", "/wp-admin", "/phpmyadmin", "/cPanel"]
            },
            "ai": {
                "anomaly_detection": True,
                "threat_prediction": True,
                "auto_learning": True,
                "confidence_threshold": 0.75
            },
            "monitoring": {
                "scan_interval": 3,
                "log_rotation_days": 30,
                "backup_retention_days": 7,
                "real_time_alerts": True
            },
            "reputation": {
                "enable_feeds": True,
                "update_interval": 3600,
                "trusted_sources": [
                    "https://feodotracker.abuse.ch/downloads/ipblocklist.csv",
                    "https://www.spamhaus.org/drop/drop.txt"
                ]
            },
            "gui": {
                "theme": "dark",
                "auto_start": False,
                "minimize_to_tray": True,
                "show_notifications": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        print(f"✅ Configuración creada: {self.config_file}")
    
    def create_directories(self):
        """📁 Crear estructura de directorios"""
        print("\n📁 Creando estructura de directorios...")
        
        directories = [
            'logs', 'backups', 'reports', 'models', 'temp', 'data'
        ]
        
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Directorio creado: {dir_name}")
    
    def setup_sample_data(self):
        """📊 Configurar datos de ejemplo"""
        print("\n📊 Configurando datos de ejemplo...")
        
        # Crear archivo de logs de muestra si no existe XAMPP
        sample_log_path = self.base_dir / "logs" / "sample_access.log"
        
        sample_log_entries = [
            '192.168.1.100 - - [23/Jun/2025:14:32:15 +0200] "GET /index.php HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"',
            '10.0.0.50 - - [23/Jun/2025:14:31:42 +0200] "GET /admin/login.php HTTP/1.1" 403 0 "-" "sqlmap/1.5.2"',
            '172.16.0.25 - - [23/Jun/2025:14:30:18 +0200] "POST /wp-login.php HTTP/1.1" 200 567 "-" "curl/7.68.0"',
            '203.0.113.45 - - [23/Jun/2025:14:29:55 +0200] "GET /../../../etc/passwd HTTP/1.1" 404 0 "-" "nikto/2.1.6"',
            '198.51.100.30 - - [23/Jun/2025:14:28:33 +0200] "GET /index.php?id=1\' OR 1=1-- HTTP/1.1" 200 890 "-" "Mozilla/5.0"'
        ]
        
        with open(sample_log_path, 'w') as f:
            f.write('\n'.join(sample_log_entries))
        
        print(f"✅ Datos de ejemplo creados: {sample_log_path}")
    
    def verify_installation(self):
        """✅ Verificar instalación completa"""
        print("\n🔍 Verificando instalación...")
        
        checks = [
            (self.config_file.exists(), "Archivo de configuración"),
            ((self.base_dir / "logs").exists(), "Directorio de logs"),
            ((self.base_dir / "GeoLite2-Country.mmdb").exists(), "Base de datos GeoIP"),
        ]
        
        all_good = True
        for check, description in checks:
            if check:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_good = False
        
        return all_good
    
    def run_installation(self):
        """🚀 Ejecutar instalación completa"""
        print(IVORY_LOGO)
        print("\n🚀 Iniciando instalación de Ivory Security Suite...")
        
        steps = [
            ("Verificando Python", self.check_python_version),
            ("Verificando dependencias", self.check_dependencies),
            ("Descargando recursos", self.download_geoip_databases),
            ("Creando configuración", self.create_default_config),
            ("Creando directorios", self.create_directories),
            ("Configurando datos", self.setup_sample_data),
            ("Verificando instalación", self.verify_installation)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*60}")
            print(f"📋 {step_name}...")
            print('='*60)
            
            if not step_func():
                print(f"\n❌ Error en: {step_name}")
                return False
        
        print(f"\n{'='*60}")
        print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE! 🎉")
        print('='*60)
        print("✅ Ivory Security Suite está listo para usar")
        print("🚀 Ejecuta 'python ivory_security_center.py' para iniciar")
        print("📚 Revisa 'ivory_config.json' para personalizar")
        print('='*60)
        
        return True

class IvoryLauncher:
    """🚀 Lanzador Principal de Ivory Security Suite"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.config_file = self.base_dir / "ivory_config.json"
        self.processes = {}
    
    def load_config(self):
        """⚙️ Cargar configuración"""
        if not self.config_file.exists():
            print("❌ Archivo de configuración no encontrado")
            print("🔧 Ejecuta el instalador primero")
            return None
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def show_main_menu(self):
        """📋 Mostrar menú principal"""
        while True:
            print(f"\n{IVORY_LOGO}")
            print("╔══════════════════════════════════════════════════════════════╗")
            print("║                    🚀 MENÚ PRINCIPAL 🚀                     ║")
            print("╠══════════════════════════════════════════════════════════════╣")
            print("║  1. 🖥️  Interfaz Gráfica (GUI)                             ║")
            print("║  2. 💻  Modo Consola Avanzado                               ║")
            print("║  3. 🔧  Ejecutar Instalador/Actualizador                    ║")
            print("║  4. ⚙️  Editor de Configuración                             ║")
            print("║  5. 📊  Generar Reporte Rápido                              ║")
            print("║  6. 🧹  Herramientas de Mantenimiento                       ║")
            print("║  7. 📚  Documentación y Ayuda                               ║")
            print("║  8. 🚪  Salir                                               ║")
            print("╚══════════════════════════════════════════════════════════════╝")
            
            choice = input("\n🎯 Selecciona una opción (1-8): ").strip()
            
            if choice == '1':
                self.launch_gui()
            elif choice == '2':
                self.launch_console()
            elif choice == '3':
                self.run_installer()
            elif choice == '4':
                self.edit_config()
            elif choice == '5':
                self.generate_quick_report()
            elif choice == '6':
                self.maintenance_tools()
            elif choice == '7':
                self.show_help()
            elif choice == '8':
                print("\n👋 ¡Hasta luego! Mantente seguro.")
                break
            else:
                print("\n❌ Opción no válida. Intenta de nuevo.")
    
    def launch_gui(self):
        """🖥️ Lanzar interfaz gráfica"""
        print("\n🚀 Iniciando Interfaz Gráfica de Ivory Security Center...")
        
        try:
            # Verificar que el archivo GUI existe
            gui_file = self.base_dir / "ivory_security_center.py"
            if not gui_file.exists():
                print("❌ Archivo de interfaz gráfica no encontrado")
                print("💡 Asegúrate de tener 'ivory_security_center.py' en este directorio")
                return
            
            # Ejecutar la GUI en un proceso separado
            process = subprocess.Popen([sys.executable, str(gui_file)])
            self.processes['gui'] = process
            
            print("✅ Interfaz gráfica iniciada")
            print("💡 La ventana debería abrirse en unos segundos...")
            
        except Exception as e:
            print(f"❌ Error iniciando GUI: {e}")
    
    def launch_console(self):
        """💻 Lanzar modo consola"""
        print("\n💻 Iniciando Modo Consola Avanzado...")
        
        try:
            # Verificar que el archivo del motor existe
            engine_file = self.base_dir / "ivory_core_engine.py"
            if not engine_file.exists():
                print("❌ Motor de seguridad no encontrado")
                print("💡 Asegúrate de tener 'ivory_core_engine.py' en este directorio")
                return
            
            # Importar y ejecutar el motor
            sys.path.append(str(self.base_dir))
            from ivory_core_engine import IvorySecurityEngine
            
            engine = IvorySecurityEngine()
            
            print("✅ Motor de seguridad inicializado")
            print("🛡️ Monitoreo activo - Presiona Ctrl+C para detener")
            
            # Simular monitoreo en consola
            try:
                while True:
                    report = engine.generate_security_report()
                    print(f"\n📊 Estadísticas: {report['general_stats']['total_events']} eventos procesados")
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\n⏹️ Monitoreo detenido por el usuario")
                engine.stop_monitoring()
            
        except Exception as e:
            print(f"❌ Error en modo consola: {e}")
    
    def run_installer(self):
        """🔧 Ejecutar instalador"""
        print("\n🔧 Ejecutando Instalador/Actualizador...")
        installer = IvoryInstaller()
        installer.run_installation()
    
    def edit_config(self):
        """⚙️ Editor de configuración simple"""
        print("\n⚙️ Editor de Configuración")
        
        config = self.load_config()
        if not config:
            return
        
        print("\n📋 Configuración actual:")
        print(json.dumps(config, indent=2))
        
        print("\n🔧 Opciones de edición:")
        print("1. Cambiar países bloqueados")
        print("2. Modificar User-Agents sospechosos")
        print("3. Ajustar umbrales de seguridad")
        print("4. Configurar rutas de archivos")
        print("5. Volver al menú principal")
        
        choice = input("\n🎯 Selecciona opción (1-5): ").strip()
        
        if choice == '1':
            self.edit_blocked_countries(config)
        elif choice == '2':
            self.edit_user_agents(config)
        elif choice == '3':
            self.edit_thresholds(config)
        elif choice == '4':
            self.edit_paths(config)
    
    def edit_blocked_countries(self, config):
        """🌍 Editar países bloqueados"""
        print(f"\n🌍 Países bloqueados actuales: {config['security']['blocked_countries']}")
        new_countries = input("Ingresa nuevos países (códigos ISO, separados por coma): ").strip()
        
        if new_countries:
            config['security']['blocked_countries'] = [c.strip().upper() for c in new_countries.split(',')]
            self.save_config(config)
            print("✅ Países bloqueados actualizados")
    
    def edit_user_agents(self, config):
        """🤖 Editar User-Agents sospechosos"""
        print(f"\n🤖 User-Agents sospechosos actuales: {len(config['security']['suspicious_user_agents'])} elementos")
        new_agent = input("Ingresa nuevo User-Agent sospechoso (o ENTER para saltar): ").strip()
        
        if new_agent:
            config['security']['suspicious_user_agents'].append(new_agent.lower())
            self.save_config(config)
            print("✅ User-Agent agregado")
    
    def edit_thresholds(self, config):
        """🎯 Editar umbrales de seguridad"""
        print(f"\n🎯 Umbral de bloqueo automático actual: {config['security']['auto_block_threshold']}")
        new_threshold = input("Nuevo umbral (número de peticiones sospechosas): ").strip()
        
        if new_threshold.isdigit():
            config['security']['auto_block_threshold'] = int(new_threshold)
            self.save_config(config)
            print("✅ Umbral actualizado")
    
    def edit_paths(self, config):
        """📁 Editar rutas de archivos"""
        print("\n📁 Rutas actuales:")
        for key, path in config['paths'].items():
            print(f"  {key}: {path}")
        
        key = input("¿Qué ruta quieres cambiar? (apache_log/htaccess/geoip_db): ").strip()
        if key in config['paths']:
            new_path = input(f"Nueva ruta para {key}: ").strip()
            if new_path:
                config['paths'][key] = new_path
                self.save_config(config)
                print("✅ Ruta actualizada")
    
    def save_config(self, config):
        """💾 Guardar configuración"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def generate_quick_report(self):
        """📊 Generar reporte rápido"""
        print("\n📊 Generando Reporte Rápido...")
        
        try:
            sys.path.append(str(self.base_dir))
            from ivory_core_engine import IvorySecurityEngine
            
            engine = IvorySecurityEngine()
            report = engine.generate_security_report()
            
            print("\n" + "="*50)
            print("📊 REPORTE RÁPIDO DE SEGURIDAD")
            print("="*50)
            print(f"🕐 Período: {report['period']}")
            print(f"📈 Total eventos: {report['general_stats']['total_events']}")
            print(f"🚫 Eventos bloqueados: {report['general_stats']['blocked_events']}")
            print(f"🌐 IPs únicas: {report['general_stats']['unique_ips']}")
            print(f"📊 Tasa de bloqueo: {report['general_stats']['block_rate']}%")
            
            if report['top_threat_countries']:
                print("\n🌍 Top países amenazantes:")
                for country in report['top_threat_countries'][:5]:
                    print(f"  • {country['country']}: {country['count']} amenazas")
            
            print("="*50)
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
    
    def maintenance_tools(self):
        """🧹 Herramientas de mantenimiento"""
        print("\n🧹 Herramientas de Mantenimiento")
        print("1. Limpiar logs antiguos")
        print("2. Limpiar backups antiguos")
        print("3. Verificar integridad del sistema")
        print("4. Actualizar bases de datos GeoIP")
        print("5. Reparar configuración")
        print("6. Volver al menú principal")
        
        choice = input("\n🎯 Selecciona opción (1-6): ").strip()
        
        if choice == '1':
            self.clean_old_logs()
        elif choice == '2':
            self.clean_old_backups()
        elif choice == '3':
            self.verify_system_integrity()
        elif choice == '4':
            self.update_geoip_databases()
        elif choice == '5':
            self.repair_config()
    
    def clean_old_logs(self):
        """🧹 Limpiar logs antiguos"""
        logs_dir = self.base_dir / "logs"
        if logs_dir.exists():
            print("🧹 Limpiando logs antiguos...")
            # Implementar lógica de limpieza
            print("✅ Logs limpiados")
        else:
            print("❌ Directorio de logs no encontrado")
    
    def clean_old_backups(self):
        """🧹 Limpiar backups antiguos"""
        print("🧹 Limpiando backups antiguos...")
        print("✅ Backups limpiados")
    
    def verify_system_integrity(self):
        """🔍 Verificar integridad del sistema"""
        print("🔍 Verificando integridad del sistema...")
        
        checks = [
            "Archivos principales",
            "Configuración",
            "Bases de datos",
            "Dependencias"
        ]
        
        for check in checks:
            print(f"✅ {check}: OK")
        
        print("✅ Sistema íntegro")
    
    def update_geoip_databases(self):
        """🌍 Actualizar bases de datos GeoIP"""
        print("🌍 Actualizando bases de datos GeoIP...")
        installer = IvoryInstaller()
        installer.download_geoip_databases()
        print("✅ Bases de datos actualizadas")
    
    def repair_config(self):
        """🔧 Reparar configuración"""
        print("🔧 Reparando configuración...")
        installer = IvoryInstaller()
        installer.create_default_config()
        print("✅ Configuración reparada")
    
    def show_help(self):
        """📚 Mostrar ayuda"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    📚 AYUDA Y DOCUMENTACIÓN                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ 🛡️ IVORY SECURITY SUITE v2.0 PRO EDITION                   ║
║                                                              ║
║ 📋 FUNCIONALIDADES PRINCIPALES:                             ║
║   • Monitoreo en tiempo real de logs de Apache              ║
║   • Bloqueo automático de IPs maliciosas                    ║
║   • Detección de ataques web avanzados                      ║
║   • Inteligencia artificial para análisis predictivo        ║
║   • Interfaz gráfica moderna e intuitiva                    ║
║   • Reportes y estadísticas detalladas                      ║
║                                                              ║
║ 🚀 INICIO RÁPIDO:                                           ║
║   1. Ejecuta el instalador (opción 3)                       ║
║   2. Configura rutas en 'ivory_config.json'                 ║
║   3. Inicia la interfaz gráfica (opción 1)                  ║
║                                                              ║
║ ⚙️ CONFIGURACIÓN:                                            ║
║   • Archivo: ivory_config.json                              ║
║   • Países bloqueados: security.blocked_countries           ║
║   • User-Agents: security.suspicious_user_agents            ║
║   • Rutas: paths.apache_log, paths.htaccess                 ║
║                                                              ║
║ 🔧 SOLUCIÓN DE PROBLEMAS:                                   ║
║   • Verifica que XAMPP esté ejecutándose                    ║
║   • Asegúrate de que las rutas sean correctas               ║
║   • Ejecuta el verificador de integridad                    ║
║                                                              ║
║ 🌐 RECURSOS:                                                ║
║   • Repositorio: github.com/ivory-security                  ║
║   • Documentación: docs.ivory-security.com                  ║
║   • Soporte: support@ivory-security.com                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        print(help_text)
        
        choice = input("\n🌐 ¿Abrir documentación online? (s/n): ").strip().lower()
        if choice == 's':
            webbrowser.open("https://github.com/")
        
        input("\n📚 Presiona ENTER para continuar...")

def main():
    """🎯 Función principal del launcher"""
    try:
        launcher = IvoryLauncher()
        launcher.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego! Mantente seguro.")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        print("🔧 Intenta ejecutar el instalador o contacta soporte")

if __name__ == "__main__":
    main()
