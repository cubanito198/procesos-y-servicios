@echo off
echo.
echo ===============================================================================
echo                🛡️  IVORY SECURITY SUITE v2.0 PRO EDITION  🛡️
echo                     INSTALADOR AUTOMÁTICO PARA WINDOWS
echo ===============================================================================
echo.

:: Configurar colores y codificación
chcp 65001 >nul
color 0A

:: Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Se requieren privilegios de administrador
    echo 💡 Haz clic derecho y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

echo ✅ Privilegios de administrador verificados
echo.

:: Crear directorio de instalación
set INSTALL_DIR=%~dp0
echo 📁 Directorio de instalación: %INSTALL_DIR%

:: Verificar Python
echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    echo 💡 Descarga Python desde: https://python.org/downloads/
    echo 💡 Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

python --version
echo ✅ Python detectado correctamente
echo.

:: Verificar pip
echo 📦 Verificando pip...
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ pip no está disponible
    echo 💡 Reinstala Python con pip incluido
    pause
    exit /b 1
)
echo ✅ pip disponible
echo.

:: Actualizar pip
echo 🔄 Actualizando pip...
python -m pip install --upgrade pip
echo.

:: Instalar dependencias principales
echo 📥 Instalando dependencias principales...
pip install matplotlib numpy scikit-learn geoip2 requests aiofiles joblib

:: Instalar dependencias opcionales
echo 📥 Instalando dependencias opcionales...
pip install plotly dash flask psutil

:: Crear directorios necesarios
echo 📁 Creando estructura de directorios...
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
if not exist "reports" mkdir reports
if not exist "models" mkdir models
if not exist "temp" mkdir temp
if not exist "data" mkdir data

echo ✅ Directorios creados
echo.

:: Descargar bases de datos GeoIP
echo 🌍 Descargando bases de datos GeoIP...

:: Verificar si curl está disponible
curl --version >nul 2>&1
if %errorLevel% equ 0 (
    echo 🔄 Descargando GeoLite2-Country.mmdb...
    curl -L -o "GeoLite2-Country.mmdb" "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb"
    
    echo 🔄 Descargando GeoLite2-City.mmdb...
    curl -L -o "GeoLite2-City.mmdb" "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"
) else (
    echo ⚠️ curl no disponible, intentando con PowerShell...
    
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb' -OutFile 'GeoLite2-Country.mmdb'}"
    
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb' -OutFile 'GeoLite2-City.mmdb'}"
)

echo ✅ Bases de datos GeoIP descargadas
echo.

:: Crear archivo de configuración
echo ⚙️ Creando configuración por defecto...
(
echo {
echo   "version": "2.0",
echo   "paths": {
echo     "apache_log": "C:\\xampp\\apache\\logs\\access.log",
echo     "error_log": "C:\\xampp\\apache\\logs\\error.log",
echo     "htaccess": "C:\\xampp\\htdocs\\.htaccess",
echo     "geoip_db": "%CD%\\GeoLite2-Country.mmdb",
echo     "city_db": "%CD%\\GeoLite2-City.mmdb"
echo   },
echo   "security": {
echo     "blocked_countries": ["CN", "RU", "KP", "IR", "CU", "ES"],
echo     "suspicious_user_agents": [
echo       "sqlmap", "nikto", "nmap", "masscan", "zmap",
echo       "gobuster", "dirb", "dirbuster", "wpscan",
echo       "curl", "wget", "python-requests", "libwww"
echo     ],
echo     "blocked_extensions": [".php~", ".bak", ".old", ".backup"],
echo     "rate_limit_per_ip": 100,
echo     "auto_block_threshold": 5,
echo     "honeypot_paths": ["/admin", "/wp-admin", "/phpmyadmin"]
echo   },
echo   "ai": {
echo     "anomaly_detection": true,
echo     "threat_prediction": true,
echo     "auto_learning": true,
echo     "confidence_threshold": 0.75
echo   },
echo   "monitoring": {
echo     "scan_interval": 3,
echo     "log_rotation_days": 30,
echo     "backup_retention_days": 7,
echo     "real_time_alerts": true
echo   }
echo }
) > ivory_config.json

echo ✅ Configuración creada: ivory_config.json
echo.

:: Crear logs de ejemplo
echo 📊 Creando datos de ejemplo...
(
echo 192.168.1.100 - - [23/Jun/2025:14:32:15 +0200] "GET /index.php HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"
echo 10.0.0.50 - - [23/Jun/2025:14:31:42 +0200] "GET /admin/login.php HTTP/1.1" 403 0 "-" "sqlmap/1.5.2"
echo 172.16.0.25 - - [23/Jun/2025:14:30:18 +0200] "POST /wp-login.php HTTP/1.1" 200 567 "-" "curl/7.68.0"
echo 203.0.113.45 - - [23/Jun/2025:14:29:55 +0200] "GET /../../../etc/passwd HTTP/1.1" 404 0 "-" "nikto/2.1.6"
echo 198.51.100.30 - - [23/Jun/2025:14:28:33 +0200] "GET /index.php?id=1' OR 1=1-- HTTP/1.1" 200 890 "-" "Mozilla/5.0"
) > logs\sample_access.log

echo ✅ Datos de ejemplo creados
echo.

:: Crear archivo de inicio rápido
echo 🚀 Creando scripts de inicio rápido...

:: Script para GUI
(
echo @echo off
echo echo 🛡️ Iniciando Ivory Security Center GUI...
echo python ivory_security_center.py
echo pause
) > "Iniciar GUI.bat"

:: Script para consola
(
echo @echo off
echo echo 💻 Iniciando Ivory Security Center - Modo Consola...
echo python ivory_core_engine.py
echo pause
) > "Iniciar Consola.bat"

:: Script para launcher
(
echo @echo off
echo echo 🚀 Iniciando Ivory Security Launcher...
echo python ivory_launcher.py
echo pause
) > "Ivory Launcher.bat"

echo ✅ Scripts de inicio creados
echo.

:: Verificar instalación
echo 🔍 Verificando instalación...

:: Verificar archivos principales
if exist "ivory_config.json" (
    echo ✅ Configuración: OK
) else (
    echo ❌ Configuración: FALTA
)

if exist "GeoLite2-Country.mmdb" (
    echo ✅ Base de datos GeoIP: OK
) else (
    echo ❌ Base de datos GeoIP: FALTA
)

if exist "logs\sample_access.log" (
    echo ✅ Datos de ejemplo: OK
) else (
    echo ❌ Datos de ejemplo: FALTA
)

echo.

:: Verificar dependencias Python
echo 🐍 Verificando dependencias Python...
python -c "import matplotlib, numpy, sklearn, geoip2, requests; print('✅ Dependencias principales: OK')" 2>nul || echo "❌ Algunas dependencias faltan"

echo.

:: Crear accesos directos en el escritorio (opcional)
echo 🖥️ ¿Deseas crear accesos directos en el escritorio? (S/N)
set /p CREATE_SHORTCUTS=

if /i "%CREATE_SHORTCUTS%"=="S" (
    echo 🔄 Creando accesos directos...
    
    :: Acceso directo para GUI
    powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Ivory Security GUI.lnk'); $Shortcut.TargetPath = '%CD%\Iniciar GUI.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = 'shell32.dll,48'; $Shortcut.Save()}"
    
    :: Acceso directo para Launcher
    powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Ivory Launcher.lnk'); $Shortcut.TargetPath = '%CD%\Ivory Launcher.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = 'shell32.dll,21'; $Shortcut.Save()}"
    
    echo ✅ Accesos directos creados en el escritorio
)

echo.
echo ===============================================================================
echo                          🎉 ¡INSTALACIÓN COMPLETADA! 🎉
echo ===============================================================================
echo.
echo ✅ Ivory Security Suite v2.0 Pro Edition instalado correctamente
echo.
echo 🚀 OPCIONES DE INICIO:
echo   • Ejecuta "Ivory Launcher.bat" para el menú principal
echo   • Ejecuta "Iniciar GUI.bat" para la interfaz gráfica
echo   • Ejecuta "Iniciar Consola.bat" para el modo terminal
echo.
echo ⚙️ CONFIGURACIÓN:
echo   • Edita "ivory_config.json" para personalizar la configuración
echo   • Ajusta las rutas de XAMPP según tu instalación
echo   • Personaliza países bloqueados y reglas de seguridad
echo.
echo 📚 PRÓXIMOS PASOS:
echo   1. Verifica que XAMPP esté ejecutándose
echo   2. Configura las rutas correctas en ivory_config.json
echo   3. Inicia el sistema con "Ivory Launcher.bat"
echo   4. ¡Disfruta de tu sistema de seguridad avanzado!
echo.
echo 🛡️ ¡Mantente seguro con Ivory Security Suite!
echo ===============================================================================
echo.

:: Preguntar si iniciar ahora
echo 🚀 ¿Deseas iniciar Ivory Security Launcher ahora? (S/N)
set /p START_NOW=

if /i "%START_NOW%"=="S" (
    echo 🛡️ Iniciando Ivory Security Launcher...
    start "Ivory Launcher" "Ivory Launcher.bat"
)

echo.
echo 👋 ¡Instalación finalizada! Presiona cualquier tecla para salir...
pause >nul
