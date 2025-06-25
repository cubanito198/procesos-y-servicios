# ivory_core_engine.py
"""
🔥 IVORY CORE ENGINE 🔥
Motor Avanzado de Seguridad Web con IA y Análisis Predictivo
Versión: 2.0 Pro Edition - Núcleo Mejorado
"""

import geoip2.database
import ipaddress
import os
import re
import shutil
import json
import hashlib
import requests
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiofiles
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# ═══════════════════════════════════════════════════════════
# 🏗️ CONFIGURACIÓN Y ESTRUCTURAS DE DATOS
# ═══════════════════════════════════════════════════════════

class ThreatLevel(Enum):
    """🚨 Niveles de amenaza"""
    LOW = "LOW"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class SecurityEvent:
    """📋 Evento de seguridad"""
    timestamp: datetime
    ip: str
    country: str
    user_agent: str
    threat_type: str
    threat_level: ThreatLevel
    request_path: str
    response_code: int
    blocked: bool = False

@dataclass
class IPIntelligence:
    """🧠 Inteligencia de IP"""
    ip: str
    country: str
    region: str
    city: str
    isp: str
    threat_score: float
    reputation_sources: List[str]
    last_seen: datetime
    attack_patterns: List[str]
    blocked_count: int = 0

class IvorySecurityEngine:
    """🛡️ Motor Principal de Seguridad Ivory"""
    
    def __init__(self, config_path: str = "ivory_config.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.setup_database()
        self.setup_ai_models()
        
        # 📊 Estadísticas en tiempo real
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'unique_ips': set(),
            'threat_countries': Counter(),
            'attack_patterns': Counter(),
            'hourly_stats': defaultdict(int)
        }
        
        # 🧠 Inteligencia de amenazas
        self.ip_intelligence: Dict[str, IPIntelligence] = {}
        self.reputation_feeds = self.load_reputation_feeds()
        
        # 🔄 Control de hilos
        self.monitoring_active = False
        self.threads = []
        
        # 📈 Modelo de Machine Learning para detección de anomalías
        self.anomaly_detector = None
        self.load_or_train_ml_model()
    
    def load_config(self, config_path: str) -> Dict:
        """⚙️ Cargar configuración avanzada"""
        default_config = {
            'paths': {
                'apache_log': r'C:\xampp\apache\logs\access.log',
                'error_log': r'C:\xampp\apache\logs\error.log',
                'htaccess': r'C:\xampp\htdocs\.htaccess',
                'geoip_db': 'GeoLite2-Country.mmdb',
                'city_db': 'GeoLite2-City.mmdb'
            },
            'security': {
                'blocked_countries': ['CN', 'RU', 'KP', 'IR', 'CU'],
                'suspicious_user_agents': [
                    'sqlmap', 'nikto', 'nmap', 'masscan', 'zmap',
                    'gobuster', 'dirb', 'dirbuster', 'wpscan',
                    'curl', 'wget', 'python-requests', 'libwww'
                ],
                'blocked_extensions': ['.php~', '.bak', '.old', '.backup'],
                'rate_limit_per_ip': 100,  # requests per minute
                'auto_block_threshold': 10,  # suspicious requests
                'honeypot_paths': ['/admin', '/wp-admin', '/phpmyadmin']
            },
            'ai': {
                'anomaly_detection': True,
                'threat_prediction': True,
                'auto_learning': True,
                'confidence_threshold': 0.8
            },
            'monitoring': {
                'scan_interval': 5,  # seconds
                'log_rotation_days': 30,
                'backup_retention_days': 7,
                'real_time_alerts': True
            },
            'reputation': {
                'enable_feeds': True,
                'update_interval': 3600,  # seconds
                'trusted_sources': [
                    'https://feodotracker.abuse.ch/downloads/ipblocklist.csv',
                    'https://reputation.alienvault.com/reputation.data'
                ]
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge configurations
                    default_config.update(user_config)
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        
        return default_config
    
    def setup_logging(self):
        """📝 Configurar sistema de logging avanzado"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('ivory_security.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IvorySecurityEngine')
    
    def setup_database(self):
        """🗄️ Configurar base de datos avanzada"""
        self.db_path = "ivory_security_advanced.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de eventos de seguridad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip TEXT NOT NULL,
                country TEXT,
                user_agent TEXT,
                request_path TEXT,
                response_code INTEGER,
                threat_type TEXT,
                threat_level TEXT,
                blocked BOOLEAN DEFAULT FALSE,
                ml_score REAL
            )
        ''')
        
        # Crear índices por separado
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_security_events_ip_timestamp 
            ON security_events(ip, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_security_events_timestamp 
            ON security_events(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_security_events_threat_level 
            ON security_events(threat_level)
        ''')
        
        # Tabla de inteligencia de IPs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_intelligence (
                ip TEXT PRIMARY KEY,
                country TEXT,
                region TEXT,
                city TEXT,
                isp TEXT,
                threat_score REAL,
                reputation_sources TEXT,
                last_seen DATETIME,
                attack_patterns TEXT,
                blocked_count INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de estadísticas por hora
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hourly_stats (
                hour_timestamp DATETIME PRIMARY KEY,
                total_requests INTEGER,
                blocked_requests INTEGER,
                unique_ips INTEGER,
                top_threat_country TEXT,
                avg_threat_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_ai_models(self):
        """🤖 Configurar modelos de IA"""
        if self.config['ai']['anomaly_detection']:
            try:
                # Intentar cargar modelo existente
                if os.path.exists('anomaly_model.pkl'):
                    self.anomaly_detector = joblib.load('anomaly_model.pkl')
                    self.logger.info("🤖 Modelo de anomalías cargado exitosamente")
                else:
                    self.logger.info("🤖 Entrenando nuevo modelo de anomalías...")
                    self.train_anomaly_model()
            except Exception as e:
                self.logger.error(f"❌ Error configurando IA: {e}")
    
    def load_reputation_feeds(self) -> Dict[str, Set[str]]:
        """🌐 Cargar feeds de reputación de IPs"""
        feeds = {'malicious_ips': set(), 'tor_nodes': set(), 'botnets': set()}
        
        if not self.config['reputation']['enable_feeds']:
            return feeds
        
        try:
            # Simulación de carga de feeds (en producción, descargar desde URLs)
            sample_malicious_ips = [
                '1.2.3.4', '5.6.7.8', '9.10.11.12', 
                '192.168.100.100', '10.0.0.200'
            ]
            feeds['malicious_ips'].update(sample_malicious_ips)
            self.logger.info(f"🌐 Cargados {len(feeds['malicious_ips'])} IPs maliciosos")
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando feeds de reputación: {e}")
        
        return feeds
    
    def train_anomaly_model(self):
        """🎓 Entrenar modelo de detección de anomalías"""
        try:
            # Generar datos de entrenamiento simulados
            # En producción, usar datos históricos reales
            normal_patterns = np.random.normal(0, 1, (1000, 5))
            anomaly_patterns = np.random.normal(3, 2, (50, 5))
            
            training_data = np.vstack([normal_patterns, anomaly_patterns])
            
            # Entrenar Isolation Forest
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.anomaly_detector.fit(training_data)
            
            # Guardar modelo
            joblib.dump(self.anomaly_detector, 'anomaly_model.pkl')
            self.logger.info("🎓 Modelo de anomalías entrenado y guardado")
            
        except Exception as e:
            self.logger.error(f"❌ Error entrenando modelo IA: {e}")
    
    def load_or_train_ml_model(self):
        """🧠 Cargar o entrenar modelo de ML"""
        model_path = 'threat_prediction_model.pkl'
        if os.path.exists(model_path):
            try:
                self.threat_predictor = joblib.load(model_path)
                self.logger.info("🧠 Modelo de predicción de amenazas cargado")
            except:
                self.train_threat_prediction_model()
        else:
            self.train_threat_prediction_model()
    
    def train_threat_prediction_model(self):
        """🎯 Entrenar modelo de predicción de amenazas"""
        # Implementación simplificada - en producción usar datos reales
        from sklearn.ensemble import RandomForestClassifier
        
        # Características: [requests_per_minute, unique_paths, error_rate, geo_risk, ua_risk]
        X_train = np.random.rand(1000, 5)
        y_train = np.random.choice([0, 1], 1000, p=[0.8, 0.2])  # 20% amenazas
        
        self.threat_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.threat_predictor.fit(X_train, y_train)
        
        joblib.dump(self.threat_predictor, 'threat_prediction_model.pkl')
        self.logger.info("🎯 Modelo de predicción entrenado")
    
    async def process_log_line_advanced(self, line: str) -> Optional[SecurityEvent]:
        """🔍 Procesamiento avanzado de línea de log"""
        # Patrón Apache Common Log Format + Combined
        pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(.*?)" (\d+) (\d+|-) "(.*?)" "(.*?)"'
        match = re.match(pattern, line)
        
        if not match:
            return None
        
        ip, timestamp_str, request, status_code, size, referer, user_agent = match.groups()
        
        try:
            # Validar IP
            ipaddress.ip_address(ip)
            
            # Obtener información geográfica
            country_info = self.get_geo_info(ip)
            
            # Analizar amenaza
            threat_analysis = self.analyze_threat(ip, user_agent, request, int(status_code))
            
            # Crear evento de seguridad
            event = SecurityEvent(
                timestamp=datetime.now(),
                ip=ip,
                country=country_info.get('country', 'Unknown'),
                user_agent=user_agent,
                threat_type=threat_analysis['type'],
                threat_level=threat_analysis['level'],
                request_path=request.split()[1] if len(request.split()) > 1 else '',
                response_code=int(status_code)
            )
            
            # Actualizar estadísticas
            self.update_real_time_stats(event)
            
            return event
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando línea: {e}")
            return None
    
    def get_geo_info(self, ip: str) -> Dict[str, str]:
        """🌍 Obtener información geográfica de IP"""
        try:
            with geoip2.database.Reader(self.config['paths']['geoip_db']) as reader:
                response = reader.country(ip)
                
                geo_info = {
                    'country': response.country.name or 'Unknown',
                    'country_code': response.country.iso_code or 'XX',
                    'continent': response.continent.name or 'Unknown'
                }
                
                # Intentar obtener información de ciudad si está disponible
                try:
                    with geoip2.database.Reader(self.config['paths']['city_db']) as city_reader:
                        city_response = city_reader.city(ip)
                        geo_info.update({
                            'city': city_response.city.name or 'Unknown',
                            'region': city_response.subdivisions.most_specific.name or 'Unknown'
                        })
                except:
                    pass
                
                return geo_info
                
        except Exception as e:
            return {'country': 'Unknown', 'country_code': 'XX'}
    
    def analyze_threat(self, ip: str, user_agent: str, request: str, status_code: int) -> Dict:
        """🎯 Análisis avanzado de amenazas con IA"""
        threat_score = 0.0
        threat_type = "Normal"
        threat_indicators = []
        
        # 1. Verificar reputación de IP
        if ip in self.reputation_feeds['malicious_ips']:
            threat_score += 0.8
            threat_indicators.append("IP en lista negra")
        
        # 2. Analizar User Agent sospechoso
        ua_lower = user_agent.lower()
        for suspicious_ua in self.config['security']['suspicious_user_agents']:
            if suspicious_ua in ua_lower:
                threat_score += 0.6
                threat_indicators.append(f"User-Agent sospechoso: {suspicious_ua}")
                threat_type = "Bot Malicioso"
        
        # 3. Verificar país bloqueado
        geo_info = self.get_geo_info(ip)
        if geo_info.get('country_code') in self.config['security']['blocked_countries']:
            threat_score += 0.5
            threat_indicators.append(f"País bloqueado: {geo_info.get('country')}")
            threat_type = "Geo-Block"
        
        # 4. Detectar patrones de ataque
        if any(pattern in request.lower() for pattern in ['../../../', 'union select', '<script>', 'php://input']):
            threat_score += 0.9
            threat_indicators.append("Patrón de ataque detectado")
            threat_type = "Ataque Web"
        
        # 5. Analizar códigos de error sospechosos
        if status_code in [401, 403, 404] and 'admin' in request.lower():
            threat_score += 0.4
            threat_indicators.append("Acceso no autorizado")
        
        # 6. Verificar paths honeypot
        for honeypot in self.config['security']['honeypot_paths']:
            if honeypot in request:
                threat_score += 0.7
                threat_indicators.append(f"Honeypot activado: {honeypot}")
                threat_type = "Reconocimiento"
        
        # 7. Usar IA para detectar anomalías
        if self.anomaly_detector and self.config['ai']['anomaly_detection']:
            try:
                # Crear vector de características
                features = self.extract_ml_features(ip, user_agent, request, status_code)
                anomaly_score = self.anomaly_detector.decision_function([features])[0]
                
                if anomaly_score < -0.5:  # Threshold para anomalía
                    threat_score += 0.6
                    threat_indicators.append(f"IA: Anomalía detectada (score: {anomaly_score:.3f})")
                    if threat_type == "Normal":
                        threat_type = "Anomalía"
            
            except Exception as e:
                self.logger.error(f"Error en análisis IA: {e}")
        
        # Determinar nivel de amenaza
        if threat_score >= 0.8:
            threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.3:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        return {
            'type': threat_type,
            'level': threat_level,
            'score': threat_score,
            'indicators': threat_indicators
        }
    
    def extract_ml_features(self, ip: str, user_agent: str, request: str, status_code: int) -> List[float]:
        """🔢 Extraer características para ML"""
        features = []
        
        # Feature 1: Longitud del User-Agent (normalizada)
        features.append(min(len(user_agent) / 200.0, 1.0))
        
        # Feature 2: Número de caracteres especiales en request
        special_chars = sum(1 for c in request if c in '!@#$%^&*()[]{}|;:,.<>?')
        features.append(min(special_chars / 50.0, 1.0))
        
        # Feature 3: Es código de error (0 o 1)
        features.append(1.0 if status_code >= 400 else 0.0)
        
        # Feature 4: Longitud del path (normalizada)
        path_part = request.split()[1] if len(request.split()) > 1 else ''
        features.append(min(len(path_part) / 100.0, 1.0))
        
        # Feature 5: Hora del día (0-1, donde 0.5 es mediodía)
        hour = datetime.now().hour
        features.append(hour / 24.0)
        
        return features
    
    def update_real_time_stats(self, event: SecurityEvent):
        """📊 Actualizar estadísticas en tiempo real"""
        self.stats['total_requests'] += 1
        self.stats['unique_ips'].add(event.ip)
        
        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self.stats['blocked_requests'] += 1
            self.stats['threat_countries'][event.country] += 1
            self.stats['attack_patterns'][event.threat_type] += 1
        
        hour_key = event.timestamp.strftime('%Y-%m-%d %H:00:00')
        self.stats['hourly_stats'][hour_key] += 1
    
    def should_block_ip(self, event: SecurityEvent) -> bool:
        """🚫 Determinar si se debe bloquear una IP"""
        # Bloqueo automático basado en nivel de amenaza
        if event.threat_level == ThreatLevel.CRITICAL:
            return True
        
        if event.threat_level == ThreatLevel.HIGH:
            # Verificar historial de la IP
            ip_history = self.get_ip_history(event.ip)
            if ip_history['suspicious_requests'] >= self.config['security']['auto_block_threshold']:
                return True
        
        # Verificar rate limiting
        if self.check_rate_limit(event.ip):
            return True
        
        return False
    
    def get_ip_history(self, ip: str) -> Dict:
        """📋 Obtener historial de una IP"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener estadísticas de las últimas 24 horas
        yesterday = datetime.now() - timedelta(days=1)
        cursor.execute('''
            SELECT COUNT(*) as total_requests,
                   SUM(CASE WHEN threat_level IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) as suspicious_requests,
                   MAX(ml_score) as max_threat_score
            FROM security_events 
            WHERE ip = ? AND timestamp > ?
        ''', (ip, yesterday))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_requests': result[0] or 0,
            'suspicious_requests': result[1] or 0,
            'max_threat_score': result[2] or 0.0
        }
    
    def check_rate_limit(self, ip: str) -> bool:
        """⏰ Verificar límite de velocidad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contar requests en el último minuto
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE ip = ? AND timestamp > ?
        ''', (ip, one_minute_ago))
        
        request_count = cursor.fetchone()[0]
        conn.close()
        
        return request_count > self.config['security']['rate_limit_per_ip']
    
    def update_htaccess_advanced(self, blocked_ips: Set[str]):
        """🔧 Actualización avanzada de .htaccess con backup inteligente"""
        htaccess_path = self.config['paths']['htaccess']
        
        try:
            # Crear backup con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{htaccess_path}.backup_{timestamp}"
            
            if os.path.exists(htaccess_path):
                shutil.copy2(htaccess_path, backup_path)
                self.logger.info(f"💾 Backup creado: {backup_path}")
            
            # Leer contenido existente
            content_lines = []
            if os.path.exists(htaccess_path):
                with open(htaccess_path, 'r', encoding='utf-8') as f:
                    content_lines = f.readlines()
            
            # Marcadores mejorados
            start_marker = "# BEGIN IVORY SECURITY ENGINE v2.0\n"
            end_marker = "# END IVORY SECURITY ENGINE v2.0\n"
            
            # Filtrar contenido existente
            new_content = []
            in_ivory_block = False
            existing_ips = set()
            
            for line in content_lines:
                if start_marker.strip() in line:
                    in_ivory_block = True
                elif end_marker.strip() in line:
                    in_ivory_block = False
                elif not in_ivory_block:
                    new_content.append(line)
                elif "Require not ip" in line:
                    # Extraer IP existente
                    ip_match = re.search(r'Require not ip (\S+)', line)
                    if ip_match:
                        existing_ips.add(ip_match.group(1))
            
            # Combinar IPs existentes con nuevas
            all_blocked_ips = existing_ips.union(blocked_ips)
            
            if all_blocked_ips:
                # Generar nuevo bloque de seguridad
                security_block = [
                    f"\n{start_marker}",
                    "# Auto-generated by Ivory Security Engine\n",
                    f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                    f"# Total blocked IPs: {len(all_blocked_ips)}\n",
                    "<RequireAll>\n",
                    "    Require all granted\n"
                ]
                
                # Añadir IPs bloqueadas ordenadas
                for ip in sorted(all_blocked_ips):
                    security_block.append(f"    Require not ip {ip}\n")
                
                security_block.extend([
                    "</RequireAll>\n",
                    end_marker
                ])
                
                # Escribir archivo actualizado
                new_content.extend(security_block)
                
                with open(htaccess_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_content)
                
                self.logger.info(f"✅ .htaccess actualizado: {len(all_blocked_ips)} IPs bloqueadas")
                
                # Limpiar backups antiguos
                self.cleanup_old_backups(htaccess_path)
                
        except Exception as e:
            self.logger.error(f"❌ Error actualizando .htaccess: {e}")
            # Restaurar backup en caso de error
            if 'backup_path' in locals() and os.path.exists(backup_path):
                shutil.copy2(backup_path, htaccess_path)
                self.logger.info("🔄 Backup restaurado debido a error")
    
    def cleanup_old_backups(self, htaccess_path: str):
        """🧹 Limpiar backups antiguos"""
        try:
            backup_dir = os.path.dirname(htaccess_path)
            backup_files = []
            
            for file in os.listdir(backup_dir):
                if file.startswith(os.path.basename(htaccess_path) + '.backup_'):
                    full_path = os.path.join(backup_dir, file)
                    backup_files.append((full_path, os.path.getmtime(full_path)))
            
            # Ordenar por fecha y mantener solo los últimos N backups
            backup_files.sort(key=lambda x: x[1], reverse=True)
            retention_days = self.config['monitoring']['backup_retention_days']
            
            for backup_path, mtime in backup_files[retention_days:]:
                os.remove(backup_path)
                self.logger.info(f"🗑️ Backup eliminado: {os.path.basename(backup_path)}")
                
        except Exception as e:
            self.logger.error(f"❌ Error limpiando backups: {e}")
    
    def generate_security_report(self) -> Dict:
        """📊 Generar reporte avanzado de seguridad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('''
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT ip) as unique_ips,
                SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked_events,
                AVG(ml_score) as avg_threat_score
            FROM security_events 
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        
        general_stats = cursor.fetchone()
        
        # Top países amenazantes
        cursor.execute('''
            SELECT country, COUNT(*) as count 
            FROM security_events 
            WHERE threat_level IN ('HIGH', 'CRITICAL') 
            AND timestamp > datetime('now', '-24 hours')
            GROUP BY country 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        
        top_threat_countries = cursor.fetchall()
        
        # Tipos de amenazas más comunes
        cursor.execute('''
            SELECT threat_type, COUNT(*) as count 
            FROM security_events 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY threat_type 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        
        top_threat_types = cursor.fetchall()
        
        conn.close()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': '24 hours',
            'general_stats': {
                'total_events': general_stats[0] or 0,
                'unique_ips': general_stats[1] or 0,
                'blocked_events': general_stats[2] or 0,
                'avg_threat_score': round(general_stats[3] or 0.0, 3),
                'block_rate': round((general_stats[2] or 0) / max(general_stats[0] or 1, 1) * 100, 2)
            },
            'top_threat_countries': [{'country': row[0], 'count': row[1]} for row in top_threat_countries],
            'top_threat_types': [{'type': row[0], 'count': row[1]} for row in top_threat_types],
            'system_health': {
                'monitoring_active': self.monitoring_active,
                'ml_model_loaded': self.anomaly_detector is not None,
                'reputation_feeds_count': len(self.reputation_feeds['malicious_ips']),
                'config_version': '2.0'
            }
        }
        
        return report
    
    def export_threat_intelligence(self, format_type: str = 'json') -> str:
        """📤 Exportar inteligencia de amenazas"""
        report = self.generate_security_report()
        
        if format_type.lower() == 'json':
            output_file = f"ivory_threat_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif format_type.lower() == 'csv':
            import csv
            output_file = f"ivory_threat_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Country', 'Threat Count'])
                for country_data in report['top_threat_countries']:
                    writer.writerow([country_data['country'], country_data['count']])
        
        self.logger.info(f"📤 Inteligencia exportada: {output_file}")
        return output_file
    
    async def start_advanced_monitoring(self):
        """🚀 Iniciar monitoreo avanzado con procesamiento asíncrono"""
        self.monitoring_active = True
        self.logger.info("🛡️ Iniciando monitoreo avanzado de seguridad...")
        
        tasks = [
            self.log_monitor_task(),
            self.reputation_update_task(),
            self.stats_aggregation_task(),
            self.ml_retraining_task()
        ]
        
        await asyncio.gather(*tasks)
    
    async def log_monitor_task(self):
        """📊 Tarea de monitoreo de logs"""
        log_path = self.config['paths']['apache_log']
        
        while self.monitoring_active:
            try:
                if os.path.exists(log_path):
                    # Procesar nuevas líneas del log
                    async with aiofiles.open(log_path, 'r') as f:
                        await f.seek(0, 2)  # Ir al final del archivo
                        
                        while self.monitoring_active:
                            line = await f.readline()
                            if line:
                                event = await self.process_log_line_advanced(line.strip())
                                if event and self.should_block_ip(event):
                                    await self.block_ip_advanced(event.ip, event)
                            else:
                                await asyncio.sleep(1)
                
                await asyncio.sleep(self.config['monitoring']['scan_interval'])
                
            except Exception as e:
                self.logger.error(f"❌ Error en monitoreo de logs: {e}")
                await asyncio.sleep(5)
    
    async def block_ip_advanced(self, ip: str, event: SecurityEvent):
        """🚫 Bloqueo avanzado de IP"""
        try:
            # Marcar evento como bloqueado
            event.blocked = True
            
            # Guardar en base de datos
            await self.save_security_event(event)
            
            # Actualizar .htaccess
            self.update_htaccess_advanced({ip})
            
            # Enviar alerta si está habilitada
            if self.config['monitoring']['real_time_alerts']:
                await self.send_real_time_alert(event)
            
            self.logger.warning(f"🚫 IP bloqueada: {ip} - {event.threat_type} ({event.threat_level.value})")
            
        except Exception as e:
            self.logger.error(f"❌ Error bloqueando IP {ip}: {e}")
    
    async def save_security_event(self, event: SecurityEvent):
        """💾 Guardar evento de seguridad en base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events 
            (ip, country, user_agent, request_path, response_code, 
             threat_type, threat_level, blocked, ml_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.ip, event.country, event.user_agent, event.request_path,
            event.response_code, event.threat_type, event.threat_level.value,
            event.blocked, 0.0  # ML score placeholder
        ))
        
        conn.commit()
        conn.close()
    
    async def send_real_time_alert(self, event: SecurityEvent):
        """🚨 Enviar alerta en tiempo real"""
        alert_message = f"""
        🚨 IVORY SECURITY ALERT 🚨
        
        Amenaza Detectada: {event.threat_type}
        Nivel: {event.threat_level.value}
        IP: {event.ip}
        País: {event.country}
        Tiempo: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        User-Agent: {event.user_agent[:50]}...
        
        Acción: IP BLOQUEADA AUTOMÁTICAMENTE
        """
        
        # Aquí se podría integrar con sistemas de notificación
        # como Slack, Discord, email, etc.
        self.logger.critical(alert_message)
    
    async def reputation_update_task(self):
        """🌐 Tarea de actualización de feeds de reputación"""
        while self.monitoring_active:
            try:
                # Actualizar feeds cada hora
                await asyncio.sleep(self.config['reputation']['update_interval'])
                self.reputation_feeds = self.load_reputation_feeds()
                self.logger.info("🌐 Feeds de reputación actualizados")
                
            except Exception as e:
                self.logger.error(f"❌ Error actualizando reputación: {e}")
    
    async def stats_aggregation_task(self):
        """📈 Tarea de agregación de estadísticas"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(3600)  # Cada hora
                # Agregar estadísticas por hora
                self.aggregate_hourly_stats()
                self.logger.info("📈 Estadísticas agregadas")
                
            except Exception as e:
                self.logger.error(f"❌ Error agregando estadísticas: {e}")
    
    async def ml_retraining_task(self):
        """🤖 Tarea de reentrenamiento de IA"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(86400)  # Cada 24 horas
                
                if self.config['ai']['auto_learning']:
                    # Reentrenar modelo con nuevos datos
                    self.retrain_models_with_new_data()
                    self.logger.info("🤖 Modelos de IA reentrenados")
                
            except Exception as e:
                self.logger.error(f"❌ Error reentrenando IA: {e}")
    
    def aggregate_hourly_stats(self):
        """📊 Agregar estadísticas por hora"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        cursor.execute('''
            INSERT OR REPLACE INTO hourly_stats 
            (hour_timestamp, total_requests, blocked_requests, unique_ips, avg_threat_score)
            SELECT 
                ? as hour_timestamp,
                COUNT(*) as total_requests,
                SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked_requests,
                COUNT(DISTINCT ip) as unique_ips,
                AVG(ml_score) as avg_threat_score
            FROM security_events 
            WHERE timestamp >= ? AND timestamp < ?
        ''', (current_hour, current_hour, current_hour + timedelta(hours=1)))
        
        conn.commit()
        conn.close()
    
    def retrain_models_with_new_data(self):
        """🎓 Reentrenar modelos con datos nuevos"""
        try:
            # Obtener datos recientes para reentrenamiento
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ip, user_agent, request_path, response_code, threat_level, blocked
                FROM security_events 
                WHERE timestamp > datetime('now', '-7 days')
                LIMIT 1000
            ''')
            
            recent_data = cursor.fetchall()
            conn.close()
            
            if len(recent_data) > 100:  # Suficientes datos para reentrenar
                # Preparar datos para entrenamiento
                X = []
                y = []
                
                for row in recent_data:
                    ip, user_agent, request_path, response_code, threat_level, blocked = row
                    features = self.extract_ml_features(ip, user_agent or '', request_path or '', response_code or 200)
                    X.append(features)
                    y.append(1 if blocked else 0)
                
                # Reentrenar modelo de anomalías
                if len(X) > 50:
                    self.anomaly_detector.fit(X)
                    joblib.dump(self.anomaly_detector, 'anomaly_model.pkl')
                    
                    self.logger.info(f"🎓 Modelo reentrenado con {len(X)} nuevos ejemplos")
            
        except Exception as e:
            self.logger.error(f"❌ Error reentrenando modelos: {e}")
    
    def stop_monitoring(self):
        """⏹️ Detener monitoreo"""
        self.monitoring_active = False
        self.logger.info("⏹️ Monitoreo de seguridad detenido")

# ═══════════════════════════════════════════════════════════
# 🚀 FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════

def main():
    """🎯 Función principal para pruebas"""
    print("🛡️ Iniciando Ivory Security Engine...")
    
    engine = IvorySecurityEngine()
    
    # Generar reporte de prueba
    report = engine.generate_security_report()
    print(f"📊 Reporte generado: {json.dumps(report, indent=2)}")
    
    # Exportar inteligencia
    intel_file = engine.export_threat_intelligence('json')
    print(f"📤 Inteligencia exportada: {intel_file}")

if __name__ == "__main__":
    main()
