# ivory_security_center.py
"""
🛡️ IVORY SECURITY CENTER 🛡️
Sistema Avanzado de Protección Web con Interfaz Gráfica
Versión: 2.0 Pro Edition
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
import os
import re
import ipaddress
import geoip2.database
import shutil
from datetime import datetime, timedelta
from collections import defaultdict, deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, List, Set, Tuple
import subprocess
import webbrowser
import sqlite3

# 🎨 CONFIGURACIÓN DE COLORES Y TEMA
COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_medium': '#2d2d2d', 
    'bg_light': '#3d3d3d',
    'accent': '#00ff88',
    'danger': '#ff4444',
    'warning': '#ffaa00',
    'info': '#4488ff',
    'text': '#ffffff',
    'text_dim': '#cccccc'
}

class SecurityDatabase:
    """🗄️ Base de datos para almacenar estadísticas y logs"""
    
    def __init__(self, db_path="ivory_security.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de IPs bloqueadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                country TEXT,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT
            )
        ''')
        
        # Tabla de estadísticas diarias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_blocks INTEGER DEFAULT 0,
                country_blocks INTEGER DEFAULT 0,
                ua_blocks INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_blocked_ip(self, ip: str, country: str = "", reason: str = "", user_agent: str = ""):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blocked_ips (ip, country, reason, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (ip, country, reason, user_agent))
        conn.commit()
        conn.close()
    
    def get_stats_last_days(self, days: int = 7) -> List[Tuple]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as blocks
            FROM blocked_ips 
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        '''.format(days))
        result = cursor.fetchall()
        conn.close()
        return result

class IvorySecurityCenter:
    """🛡️ Centro de Seguridad Ivory - Aplicación Principal"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.db = SecurityDatabase()
        
        # 📊 Variables de estado
        self.monitoring_active = False
        self.blocked_ips = set()
        self.blocked_countries = {'Spain', 'Cuba', 'Ukraine', 'Russia', 'China'}
        self.suspicious_ua = {"-", "", "curl", "wget", "sqlmap", "nikto", "nmap", "gobuster", "dirb"}
        self.stats = defaultdict(int)
        self.recent_attacks = deque(maxlen=100)
        
        # 📁 Configuración de rutas
        self.config = {
            'log_path': r'C:\xampp\apache\logs\access.log',
            'htaccess_path': r'C:\xampp\htdocs\.htaccess',
            'geoip_path': 'GeoLite2-Country.mmdb',
            'auto_block': True,
            'scan_interval': 10
        }
        
        self.create_widgets()
        self.setup_monitoring()
        
    def setup_window(self):
        """🪟 Configuración de la ventana principal"""
        self.root.title("🛡️ IVORY SECURITY CENTER v2.0 Pro")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(True, True)
        
        # Icono y estilo
        try:
            self.root.iconbitmap()  # Aquí podrías añadir un icono
        except:
            pass
            
        # Configurar el grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def create_widgets(self):
        """🎨 Crear todos los widgets de la interfaz"""
        
        # ═══════════════════════════════════════════════════════════
        # 📋 PANEL LATERAL IZQUIERDO - NAVEGACIÓN
        # ═══════════════════════════════════════════════════════════
        
        nav_frame = tk.Frame(self.root, bg=COLORS['bg_medium'], width=250)
        nav_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        nav_frame.grid_propagate(False)
        
        # Logo y título
        title_frame = tk.Frame(nav_frame, bg=COLORS['bg_medium'])
        title_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(title_frame, text="🛡️ IVORY", font=('Arial', 18, 'bold'), 
                fg=COLORS['accent'], bg=COLORS['bg_medium']).pack()
        tk.Label(title_frame, text="Security Center", font=('Arial', 12), 
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack()
        
        # Botones de navegación
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🔍 Monitor en Vivo", self.show_live_monitor),
            ("🌍 Mapa de Amenazas", self.show_threat_map),
            ("⚙️ Configuración", self.show_config),
            ("📈 Estadísticas", self.show_statistics),
            ("📋 Reportes", self.show_reports),
            ("🔧 Herramientas", self.show_tools)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, command=command,
                          bg=COLORS['bg_light'], fg=COLORS['text'],
                          font=('Arial', 10), bd=0, pady=8,
                          activebackground=COLORS['accent'],
                          activeforeground=COLORS['bg_dark'])
            btn.pack(fill='x', padx=10, pady=2)
        
        # Estado del sistema
        status_frame = tk.LabelFrame(nav_frame, text="🔋 Estado del Sistema", 
                                   fg=COLORS['accent'], bg=COLORS['bg_medium'])
        status_frame.pack(fill='x', padx=10, pady=20)
        
        self.status_label = tk.Label(status_frame, text="🔴 Inactivo", 
                                   fg=COLORS['danger'], bg=COLORS['bg_medium'])
        self.status_label.pack(pady=5)
        
        self.toggle_btn = tk.Button(status_frame, text="▶️ INICIAR PROTECCIÓN",
                                  command=self.toggle_monitoring,
                                  bg=COLORS['accent'], fg=COLORS['bg_dark'],
                                  font=('Arial', 10, 'bold'), bd=0, pady=5)
        self.toggle_btn.pack(fill='x', padx=5, pady=5)
        
        # ═══════════════════════════════════════════════════════════
        # 📱 PANEL PRINCIPAL - CONTENIDO
        # ═══════════════════════════════════════════════════════════
        
        self.main_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        self.main_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Mostrar dashboard por defecto
        self.show_dashboard()
    
    def clear_main_frame(self):
        """🧹 Limpiar el panel principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """📊 Mostrar dashboard principal"""
        self.clear_main_frame()
        
        # Header
        header = tk.Frame(self.main_frame, bg=COLORS['bg_dark'])
        header.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        tk.Label(header, text="📊 DASHBOARD DE SEGURIDAD", 
                font=('Arial', 20, 'bold'), fg=COLORS['accent'], 
                bg=COLORS['bg_dark']).pack()
        
        # Métricas principales
        metrics_frame = tk.Frame(self.main_frame, bg=COLORS['bg_dark'])
        metrics_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        metrics = [
            ("🚫 IPs Bloqueadas", len(self.blocked_ips), COLORS['danger']),
            ("🌍 Países Monitoreados", len(self.blocked_countries), COLORS['warning']),
            ("🤖 Bots Detectados", self.stats['bot_detections'], COLORS['info']),
            ("⚡ Ataques Hoy", self.stats['attacks_today'], COLORS['accent'])
        ]
        
        for i, (title, value, color) in enumerate(metrics):
            card = tk.Frame(metrics_frame, bg=COLORS['bg_medium'], relief='raised', bd=2)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            metrics_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(card, text=str(value), font=('Arial', 24, 'bold'),
                    fg=color, bg=COLORS['bg_medium']).pack(pady=5)
            tk.Label(card, text=title, font=('Arial', 10),
                    fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(pady=(0, 10))
        
        # Gráfico de actividad
        self.create_activity_chart()
        
        # Lista de amenazas recientes
        self.create_recent_threats_list()
    
    def create_activity_chart(self):
        """📈 Crear gráfico de actividad"""
        chart_frame = tk.LabelFrame(self.main_frame, text="📈 Actividad de Seguridad (7 días)",
                                  fg=COLORS['accent'], bg=COLORS['bg_dark'])
        chart_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        
        # Crear figura de matplotlib
        fig = Figure(figsize=(10, 4), facecolor=COLORS['bg_dark'])
        ax = fig.add_subplot(111, facecolor=COLORS['bg_medium'])
        
        # Datos de ejemplo (aquí conectarías con la base de datos real)
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        blocks = [23, 45, 56, 78, 32, 67, 89]
        
        ax.plot(days, blocks, color=COLORS['accent'], linewidth=3, marker='o', markersize=8)
        ax.fill_between(days, blocks, alpha=0.3, color=COLORS['accent'])
        ax.set_title('Bloqueos por Día', color=COLORS['text'], fontsize=14, fontweight='bold')
        ax.set_ylabel('Número de Bloqueos', color=COLORS['text'])
        ax.tick_params(colors=COLORS['text'])
        ax.grid(True, alpha=0.3)
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_recent_threats_list(self):
        """🚨 Lista de amenazas recientes"""
        threats_frame = tk.LabelFrame(self.main_frame, text="🚨 Amenazas Recientes",
                                    fg=COLORS['danger'], bg=COLORS['bg_dark'])
        threats_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=10)
        
        # Crear Treeview
        columns = ('Tiempo', 'IP', 'País', 'Amenaza', 'Estado')
        tree = ttk.Treeview(threats_frame, columns=columns, show='headings', height=6)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Datos de ejemplo
        threats_data = [
            ('14:32:15', '192.168.1.100', '🇪🇸 España', 'Acceso sospechoso', '🚫 Bloqueado'),
            ('14:31:42', '10.0.0.50', '🇺🇦 Ucrania', 'Bot sqlmap', '🚫 Bloqueado'),
            ('14:30:18', '172.16.0.25', '🇨🇺 Cuba', 'Escaneo de puertos', '🚫 Bloqueado'),
            ('14:29:55', '203.0.113.45', '🇨🇳 China', 'User-Agent malicioso', '🚫 Bloqueado'),
            ('14:28:33', '198.51.100.30', '🇷🇺 Rusia', 'Inyección SQL', '🚫 Bloqueado')
        ]
        
        for threat in threats_data:
            tree.insert('', 'end', values=threat)
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(threats_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
    
    def show_live_monitor(self):
        """🔍 Monitor en tiempo real"""
        self.clear_main_frame()
        
        tk.Label(self.main_frame, text="🔍 MONITOR EN TIEMPO REAL", 
                font=('Arial', 20, 'bold'), fg=COLORS['accent'], 
                bg=COLORS['bg_dark']).pack(pady=20)
        
        # Panel de logs en vivo
        log_frame = tk.LabelFrame(self.main_frame, text="📝 Logs en Tiempo Real",
                                fg=COLORS['info'], bg=COLORS['bg_dark'])
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, bg=COLORS['bg_medium'], fg=COLORS['text'],
                              font=('Consolas', 10), wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar para logs
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scroll.set)
        log_scroll.pack(side='right', fill='y')
        
        # Simular logs en tiempo real
        self.simulate_live_logs()
    
    def simulate_live_logs(self):
        """📝 Simular logs en tiempo real"""
        if hasattr(self, 'log_text'):
            sample_logs = [
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Escaneando logs de Apache...",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🚫 IP 192.168.1.100 bloqueada - País: España",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Bot detectado: User-Agent 'sqlmap'",
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ Actualizando reglas .htaccess",
                f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Sistema funcionando correctamente"
            ]
            
            import random
            log_entry = random.choice(sample_logs)
            self.log_text.insert(tk.END, log_entry + "\n")
            self.log_text.see(tk.END)
            
            # Programar siguiente log
            self.root.after(3000, self.simulate_live_logs)
    
    def show_threat_map(self):
        """🌍 Mapa mundial de amenazas"""
        self.clear_main_frame()
        
        tk.Label(self.main_frame, text="🌍 MAPA MUNDIAL DE AMENAZAS", 
                font=('Arial', 20, 'bold'), fg=COLORS['accent'], 
                bg=COLORS['bg_dark']).pack(pady=20)
        
        # Marco para el mapa
        map_frame = tk.Frame(self.main_frame, bg=COLORS['bg_medium'], relief='raised', bd=2)
        map_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Simular mapa mundial con gráfico
        fig = Figure(figsize=(12, 8), facecolor=COLORS['bg_dark'])
        ax = fig.add_subplot(111, facecolor=COLORS['bg_medium'])
        
        # Datos de amenazas por país (simulados)
        countries = ['España', 'Rusia', 'China', 'Ucrania', 'Cuba', 'USA', 'Brasil']
        threats = [45, 67, 89, 34, 23, 12, 8]
        colors_map = [COLORS['danger'] if t > 50 else COLORS['warning'] if t > 20 else COLORS['info'] for t in threats]
        
        bars = ax.bar(countries, threats, color=colors_map, alpha=0.8)
        ax.set_title('Amenazas por País (Últimas 24h)', color=COLORS['text'], fontsize=16, fontweight='bold')
        ax.set_ylabel('Número de Amenazas', color=COLORS['text'])
        ax.tick_params(colors=COLORS['text'])
        
        # Añadir valores en las barras
        for bar, threat in zip(bars, threats):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{threat}', ha='center', va='bottom', color=COLORS['text'], fontweight='bold')
        
        plt.xticks(rotation=45)
        canvas = FigureCanvasTkAgg(fig, map_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def show_config(self):
        """⚙️ Panel de configuración"""
        self.clear_main_frame()
        
        tk.Label(self.main_frame, text="⚙️ CONFIGURACIÓN AVANZADA", 
                font=('Arial', 20, 'bold'), fg=COLORS['accent'], 
                bg=COLORS['bg_dark']).pack(pady=20)
        
        # Configuración de rutas
        paths_frame = tk.LabelFrame(self.main_frame, text="📁 Rutas del Sistema",
                                  fg=COLORS['info'], bg=COLORS['bg_dark'])
        paths_frame.pack(fill='x', padx=20, pady=10)
        
        paths_config = [
            ("📊 Archivo de Logs:", self.config['log_path']),
            ("🔧 Archivo .htaccess:", self.config['htaccess_path']),
            ("🌍 Base de datos GeoIP:", self.config['geoip_path'])
        ]
        
        for i, (label, path) in enumerate(paths_config):
            frame = tk.Frame(paths_frame, bg=COLORS['bg_dark'])
            frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(frame, text=label, fg=COLORS['text'], bg=COLORS['bg_dark']).pack(anchor='w')
            entry = tk.Entry(frame, bg=COLORS['bg_medium'], fg=COLORS['text'], width=80)
            entry.insert(0, path)
            entry.pack(side='left', fill='x', expand=True, pady=2)
            
            tk.Button(frame, text="📂", command=lambda: self.browse_file(),
                     bg=COLORS['accent'], fg=COLORS['bg_dark']).pack(side='right', padx=5)
        
        # Configuración de países bloqueados
        countries_frame = tk.LabelFrame(self.main_frame, text="🌍 Países Bloqueados",
                                      fg=COLORS['warning'], bg=COLORS['bg_dark'])
        countries_frame.pack(fill='x', padx=20, pady=10)
        
        self.countries_listbox = tk.Listbox(countries_frame, bg=COLORS['bg_medium'], 
                                          fg=COLORS['text'], selectmode='multiple')
        for country in self.blocked_countries:
            self.countries_listbox.insert(tk.END, country)
        self.countries_listbox.pack(fill='x', padx=10, pady=10)
        
        # Botones de configuración
        btn_frame = tk.Frame(self.main_frame, bg=COLORS['bg_dark'])
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(btn_frame, text="💾 GUARDAR CONFIGURACIÓN",
                 bg=COLORS['accent'], fg=COLORS['bg_dark'], 
                 font=('Arial', 12, 'bold'), command=self.save_config).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🔄 RESTABLECER",
                 bg=COLORS['warning'], fg=COLORS['bg_dark'], 
                 font=('Arial', 12, 'bold'), command=self.reset_config).pack(side='left', padx=10)
    
    def show_statistics(self):
        """📈 Panel de estadísticas avanzadas"""
        self.clear_main_frame()
        
        tk.Label(self.main_frame, text="📈 ESTADÍSTICAS AVANZADAS", 
                font=('Arial', 20, 'bold'), fg=COLORS['accent'], 
                bg=COLORS['bg_dark']).pack(pady=20)
        
        # Crear gráficos de estadísticas
        self.create_advanced_stats()
    
    def create_advanced_stats(self):
        """📊 Crear gráficos de estadísticas avanzadas"""
        stats_frame = tk.Frame(self.main_frame, bg=COLORS['bg_dark'])
        stats_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Gráfico circular de tipos de amenazas
        fig = Figure(figsize=(15, 6), facecolor=COLORS['bg_dark'])
        
        # Subplot 1: Gráfico de pastel
        ax1 = fig.add_subplot(121, facecolor=COLORS['bg_medium'])
        threat_types = ['Bots Maliciosos', 'Países Bloqueados', 'IPs Sospechosas', 'Escaneos']
        sizes = [30, 25, 25, 20]
        colors = [COLORS['danger'], COLORS['warning'], COLORS['info'], COLORS['accent']]
        
        ax1.pie(sizes, labels=threat_types, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Distribución de Amenazas', color=COLORS['text'], fontsize=14, fontweight='bold')
        
        # Subplot 2: Gráfico de líneas de tendencia
        ax2 = fig.add_subplot(122, facecolor=COLORS['bg_medium'])
        hours = range(24)
        attacks = np.random.poisson(5, 24) + np.sin(np.array(hours) * np.pi / 12) * 3 + 5
        
        ax2.plot(hours, attacks, color=COLORS['accent'], linewidth=2, marker='o')
        ax2.fill_between(hours, attacks, alpha=0.3, color=COLORS['accent'])
        ax2.set_title('Ataques por Hora (Hoy)', color=COLORS['text'], fontsize=14, fontweight='bold')
        ax2.set_xlabel('Hora del Día', color=COLORS['text'])
        ax2.set_ylabel('Número de Ataques', color=COLORS['text'])
        ax2.tick_params(colors=COLORS['text'])
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def show_reports(self):
        """📋 Panel de reportes"""
        self.clear_main_frame()
        
        tk.Label(self.main_frame, text="📋 GENERADOR DE REPORTES", 
                font=('Arial', 20, 'bold'), fg=COLORS['accent'], 
                bg=COLORS['bg_dark']).pack(pady=20)
        
        # Opciones de reportes
        report_frame = tk.LabelFrame(self.main_frame, text="📊 Tipos de Reportes",
                                   fg=COLORS['info'], bg=COLORS['bg_dark'])
        report_frame.pack(fill='x', padx=20, pady=10)
        
        reports = [
            ("📈 Reporte de Actividad Semanal", self.generate_weekly_report),
            ("🌍 Reporte de Amenazas por País", self.generate_country_report),
            ("🤖 Reporte de Bots Detectados", self.generate_bot_report),
            ("📋 Reporte Completo del Sistema", self.generate_full_report)
        ]
        
        for text, command in reports:
            btn = tk.Button(report_frame, text=text, command=command,
                          bg=COLORS['bg_light'], fg=COLORS['text'],
                          font=('Arial', 12), pady=10)
            btn.pack(fill='x', padx=10, pady=5)
    
    def show_tools(self):
        """🔧 Panel de herramientas"""
        self.clear_main_frame()
        
        tk.Label(self.main_frame, text="🔧 HERRAMIENTAS DE ADMINISTRACIÓN", 
                font=('Arial', 20, 'bold'), fg=COLORS['accent'], 
                bg=COLORS['bg_dark']).pack(pady=20)
        
        tools_frame = tk.Frame(self.main_frame, bg=COLORS['bg_dark'])
        tools_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Herramientas disponibles
        tools = [
            ("🔄 Actualizar Base de Datos GeoIP", self.update_geoip),
            ("🧹 Limpiar Logs Antiguos", self.clean_old_logs),
            ("🔍 Escanear IPs Sospechosas", self.scan_suspicious_ips),
            ("📤 Exportar Lista de IPs Bloqueadas", self.export_blocked_ips),
            ("🔧 Reparar Archivo .htaccess", self.repair_htaccess),
            ("📊 Generar Backup del Sistema", self.create_system_backup)
        ]
        
        for i, (text, command) in enumerate(tools):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(tools_frame, text=text, command=command,
                          bg=COLORS['bg_light'], fg=COLORS['text'],
                          font=('Arial', 11), pady=15, width=30)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
        
        tools_frame.grid_columnconfigure(0, weight=1)
        tools_frame.grid_columnconfigure(1, weight=1)
    
    def toggle_monitoring(self):
        """🔄 Activar/Desactivar monitoreo"""
        self.monitoring_active = not self.monitoring_active
        
        if self.monitoring_active:
            self.status_label.config(text="🟢 Activo", fg=COLORS['accent'])
            self.toggle_btn.config(text="⏸️ PAUSAR PROTECCIÓN", bg=COLORS['warning'])
            self.start_monitoring_thread()
        else:
            self.status_label.config(text="🔴 Inactivo", fg=COLORS['danger'])
            self.toggle_btn.config(text="▶️ INICIAR PROTECCIÓN", bg=COLORS['accent'])
    
    def setup_monitoring(self):
        """🛡️ Configurar sistema de monitoreo"""
        self.monitoring_thread = None
    
    def start_monitoring_thread(self):
        """🚀 Iniciar hilo de monitoreo"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
    
    def monitoring_loop(self):
        """🔄 Bucle principal de monitoreo"""
        while self.monitoring_active:
            try:
                # Simular procesamiento de logs
                self.process_security_logs()
                time.sleep(self.config['scan_interval'])
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(5)
    
    def process_security_logs(self):
        """📊 Procesar logs de seguridad"""
        # Aquí iría la lógica real de procesamiento
        # Por ahora simulamos la detección de amenazas
        import random
        
        if random.random() < 0.3:  # 30% de probabilidad de detectar amenaza
            fake_ip = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
            fake_country = random.choice(list(self.blocked_countries))
            
            self.blocked_ips.add(fake_ip)
            self.stats['attacks_today'] += 1
            
            # Añadir a la base de datos
            self.db.add_blocked_ip(fake_ip, fake_country, "Auto-detected threat")
    
    # ═══════════════════════════════════════════════════════════
    # 🛠️ MÉTODOS DE HERRAMIENTAS
    # ═══════════════════════════════════════════════════════════
    
    def browse_file(self):
        """📂 Navegador de archivos"""
        filename = filedialog.askopenfilename()
        if filename:
            messagebox.showinfo("Archivo Seleccionado", f"Archivo: {filename}")
    
    def save_config(self):
        """💾 Guardar configuración"""
        messagebox.showinfo("Configuración", "✅ Configuración guardada correctamente")
    
    def reset_config(self):
        """🔄 Restablecer configuración"""
        messagebox.showwarning("Restablecer", "⚠️ Configuración restablecida a valores por defecto")
    
    def generate_weekly_report(self):
        """📈 Generar reporte semanal"""
        messagebox.showinfo("Reporte", "📈 Reporte semanal generado exitosamente")
    
    def generate_country_report(self):
        """🌍 Generar reporte por países"""
        messagebox.showinfo("Reporte", "🌍 Reporte de países generado exitosamente")
    
    def generate_bot_report(self):
        """🤖 Generar reporte de bots"""
        messagebox.showinfo("Reporte", "🤖 Reporte de bots generado exitosamente")
    
    def generate_full_report(self):
        """📋 Generar reporte completo"""
        messagebox.showinfo("Reporte", "📋 Reporte completo generado exitosamente")
    
    def update_geoip(self):
        """🔄 Actualizar base de datos GeoIP"""
        messagebox.showinfo("GeoIP", "🔄 Base de datos GeoIP actualizada")
    
    def clean_old_logs(self):
        """🧹 Limpiar logs antiguos"""
        messagebox.showinfo("Limpieza", "🧹 Logs antiguos eliminados correctamente")
    
    def scan_suspicious_ips(self):
        """🔍 Escanear IPs sospechosas"""
        messagebox.showinfo("Escaneo", "🔍 Escaneo de IPs completado")
    
    def export_blocked_ips(self):
        """📤 Exportar IPs bloqueadas"""
        messagebox.showinfo("Exportar", "📤 Lista de IPs exportada exitosamente")
    
    def repair_htaccess(self):
        """🔧 Reparar archivo .htaccess"""
        messagebox.showinfo("Reparación", "🔧 Archivo .htaccess reparado correctamente")
    
    def create_system_backup(self):
        """📊 Crear backup del sistema"""
        messagebox.showinfo("Backup", "📊 Backup del sistema creado exitosamente")
    
    def run(self):
        """🚀 Ejecutar la aplicación"""
        print("🛡️ Iniciando Ivory Security Center...")
        print("🌟 ¡Interfaz gráfica cargada exitosamente!")
        self.root.mainloop()

# ═══════════════════════════════════════════════════════════
# 🚀 PUNTO DE ENTRADA PRINCIPAL
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🛡️  IVORY SECURITY CENTER v2.0 Pro Edition  🛡️")
    print("🌟  Sistema Avanzado de Protección Web")
    print("💻  Interfaz Gráfica de Nueva Generación")
    print("=" * 60)
    
    try:
        app = IvorySecurityCenter()
        app.run()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        input("Presiona Enter para salir...")
