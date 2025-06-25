import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import psutil
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from datetime import datetime
import os
import json
from collections import deque
import queue

class NetworkMonitorGUI:
    def __init__(self):
        self.setup_data()
        self.setup_gui()
        self.setup_monitoring()
        
    def setup_data(self):
        """Inicializa variables y configuración"""
        # Configuración del monitoreo
        self.monitoring = False
        self.interval = 1.0
        self.alert_threshold = 15.0
        self.admin_notified = False
        
        # Datos para gráficos (últimos 60 puntos = 1 minuto)
        self.upload_data = deque(maxlen=60)
        self.download_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        
        # Valores de referencia
        self.baseline_upload = 0
        self.baseline_download = 0
        
        # Cola para comunicación entre threads
        self.data_queue = queue.Queue()
        
        # Log de eventos
        self.events_log = []
        
        # Configuración de email
        self.email_config = {
            'sender': '',
            'password': '',
            'receiver': '',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        }
        
        # Cargar configuración si existe
        self.load_config()
        self.load_baseline()
    
    def setup_gui(self):
        """Crea la interfaz gráfica moderna"""
        self.root = tk.Tk()
        self.root.title("Monitor de Red Avanzado")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Centrar ventana
        self.center_window(self.root, 1400, 900)
        
        # HEADER PRINCIPAL
        self.create_header()
        
        # MAIN CONTENT - Dividido en secciones
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # PANEL IZQUIERDO - Controles y configuración
        left_panel = tk.Frame(main_container, bg='#1a1a1a', width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.pack_propagate(False)
        
        self.create_control_panel(left_panel)
        
        # PANEL DERECHO - Gráficos y logs
        right_panel = tk.Frame(main_container, bg='#0a0a0a')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_monitoring_panel(right_panel)
        
        # Inicializar gráfico
        self.update_display()
    
    def center_window(self, window, width, height):
        """Centra una ventana en la pantalla"""
        # Obtener dimensiones de la pantalla
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calcular posición
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Aplicar geometría
        window.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_header(self):
        """Crea el header principal"""
        header = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 15))
        header.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header, bg='#1a1a1a')
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        # Lado izquierdo - Logo y título
        left_header = tk.Frame(header_content, bg='#1a1a1a')
        left_header.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(left_header, text="[NET]", font=('Arial', 24, 'bold'), 
                bg='#1a1a1a', fg='#00ff88').pack(side=tk.LEFT)
        
        title_frame = tk.Frame(left_header, bg='#1a1a1a')
        title_frame.pack(side=tk.LEFT, padx=(15, 0), fill=tk.Y)
        
        tk.Label(title_frame, text="Monitor de Red Avanzado", 
                font=('Arial', 20, 'bold'), bg='#1a1a1a', fg='#ffffff').pack(anchor='w')
        
        self.status_label = tk.Label(title_frame, text="● Detenido", 
                                    font=('Arial', 12), bg='#1a1a1a', fg='#dc3545')
        self.status_label.pack(anchor='w')
        
        # Lado derecho - Info del sistema
        right_header = tk.Frame(header_content, bg='#1a1a1a')
        right_header.pack(side=tk.RIGHT, fill=tk.Y)
        
        current_time = datetime.now().strftime("%H:%M - %d/%m/%Y")
        tk.Label(right_header, text=f"Fecha: {current_time}", 
                font=('Arial', 12), bg='#1a1a1a', fg='#888888').pack(anchor='e')
        
        # Obtener información de red
        try:
            net_info = psutil.net_if_addrs()
            interfaces = len([i for i in net_info.keys() if 'lo' not in i.lower()])
            tk.Label(right_header, text=f"Interfaces: {interfaces}", 
                    font=('Arial', 12), bg='#1a1a1a', fg='#888888').pack(anchor='e')
        except:
            tk.Label(right_header, text="Interfaces: N/A", 
                    font=('Arial', 12), bg='#1a1a1a', fg='#888888').pack(anchor='e')
    
    def create_control_panel(self, parent):
        """Crea el panel de control izquierdo"""
        # SECCIÓN: CONTROL DE MONITOREO
        control_section = tk.LabelFrame(parent, text="Control de Monitoreo", 
                                       font=('Arial', 12, 'bold'), bg='#1a1a1a', 
                                       fg='#ffffff', bd=2, relief='groove')
        control_section.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        # Botones de control
        buttons_frame = tk.Frame(control_section, bg='#1a1a1a')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.start_btn = tk.Button(buttons_frame, text="▶ Iniciar Monitoreo", 
                                  command=self.start_monitoring, font=('Arial', 11, 'bold'),
                                  bg='#28a745', fg='white', relief=tk.RAISED, 
                                  padx=20, pady=10, cursor='hand2', bd=2)
        self.start_btn.pack(fill=tk.X, pady=(0, 8))
        
        self.stop_btn = tk.Button(buttons_frame, text="⏹ Detener Monitoreo", 
                                 command=self.stop_monitoring, font=('Arial', 11, 'bold'),
                                 bg='#dc3545', fg='white', relief=tk.RAISED, 
                                 padx=20, pady=10, cursor='hand2', state=tk.DISABLED, bd=2)
        self.stop_btn.pack(fill=tk.X, pady=(0, 8))
        
        self.reset_btn = tk.Button(buttons_frame, text="⟲ Recalibrar Baseline", 
                                  command=self.recalibrate_baseline, font=('Arial', 11, 'bold'),
                                  bg='#007acc', fg='white', relief=tk.RAISED, 
                                  padx=20, pady=10, cursor='hand2', bd=2)
        self.reset_btn.pack(fill=tk.X)
        
        # SECCIÓN: CONFIGURACIÓN
        config_section = tk.LabelFrame(parent, text="Configuración", 
                                      font=('Arial', 12, 'bold'), bg='#1a1a1a', 
                                      fg='#ffffff', bd=2, relief='groove')
        config_section.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        config_content = tk.Frame(config_section, bg='#1a1a1a')
        config_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Intervalo de monitoreo
        tk.Label(config_content, text="Intervalo (segundos):", 
                font=('Arial', 10, 'bold'), bg='#1a1a1a', fg='#ffffff').pack(anchor='w')
        
        self.interval_var = tk.StringVar(value=str(self.interval))
        interval_entry = tk.Entry(config_content, textvariable=self.interval_var, 
                                 font=('Arial', 10), bg='#404040', fg='#ffffff',
                                 relief=tk.SUNKEN, bd=2, insertbackground='white')
        interval_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Umbral de alerta
        tk.Label(config_content, text="Umbral de alerta (x veces normal):", 
                font=('Arial', 10, 'bold'), bg='#1a1a1a', fg='#ffffff').pack(anchor='w')
        
        self.threshold_var = tk.StringVar(value=str(self.alert_threshold))
        threshold_entry = tk.Entry(config_content, textvariable=self.threshold_var, 
                                  font=('Arial', 10), bg='#404040', fg='#ffffff',
                                  relief=tk.SUNKEN, bd=2, insertbackground='white')
        threshold_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Botón configurar email
        email_btn = tk.Button(config_content, text="@ Configurar Email", 
                             command=self.configure_email, font=('Arial', 10, 'bold'),
                             bg='#6c757d', fg='white', relief=tk.RAISED, 
                             padx=15, pady=8, cursor='hand2', bd=2)
        email_btn.pack(fill=tk.X)
        
        # SECCIÓN: ESTADÍSTICAS EN TIEMPO REAL
        stats_section = tk.LabelFrame(parent, text="Estadísticas Actuales", 
                                     font=('Arial', 12, 'bold'), bg='#1a1a1a', 
                                     fg='#ffffff', bd=2, relief='groove')
        stats_section.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        stats_content = tk.Frame(stats_section, bg='#1a1a1a')
        stats_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Labels para estadísticas
        self.upload_stat = tk.Label(stats_content, text="↑ Subida: 0 KB/s", 
                                   font=('Arial', 11), bg='#1a1a1a', fg='#00ff88')
        self.upload_stat.pack(anchor='w', pady=2)
        
        self.download_stat = tk.Label(stats_content, text="↓ Descarga: 0 KB/s", 
                                     font=('Arial', 11), bg='#1a1a1a', fg='#007acc')
        self.download_stat.pack(anchor='w', pady=2)
        
        self.baseline_stat = tk.Label(stats_content, text="Baseline: No establecido", 
                                     font=('Arial', 11), bg='#1a1a1a', fg='#ffc107')
        self.baseline_stat.pack(anchor='w', pady=2)
        
        self.alerts_stat = tk.Label(stats_content, text="Alertas: 0", 
                                   font=('Arial', 11), bg='#1a1a1a', fg='#dc3545')
        self.alerts_stat.pack(anchor='w', pady=2)
        
        # SECCIÓN: ACCIONES RÁPIDAS
        actions_section = tk.LabelFrame(parent, text="Acciones Rápidas", 
                                       font=('Arial', 12, 'bold'), bg='#1a1a1a', 
                                       fg='#ffffff', bd=2, relief='groove')
        actions_section.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        actions_content = tk.Frame(actions_section, bg='#1a1a1a')
        actions_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Botones de acción
        test_btn = tk.Button(actions_content, text="Test Email", 
                            command=self.test_email, font=('Arial', 10),
                            bg='#17a2b8', fg='white', relief=tk.RAISED, 
                            padx=15, pady=6, cursor='hand2', bd=2)
        test_btn.pack(fill=tk.X, pady=(0, 5))
        
        export_btn = tk.Button(actions_content, text="Exportar Logs", 
                              command=self.export_logs, font=('Arial', 10),
                              bg='#6f42c1', fg='white', relief=tk.RAISED, 
                              padx=15, pady=6, cursor='hand2', bd=2)
        export_btn.pack(fill=tk.X, pady=(0, 5))
        
        clear_btn = tk.Button(actions_content, text="Limpiar Logs", 
                             command=self.clear_logs, font=('Arial', 10),
                             bg='#fd7e14', fg='white', relief=tk.RAISED, 
                             padx=15, pady=6, cursor='hand2', bd=2)
        clear_btn.pack(fill=tk.X)
    
    def create_monitoring_panel(self, parent):
        """Crea el panel de monitoreo derecho"""
        # SECCIÓN: GRÁFICO EN TIEMPO REAL
        graph_section = tk.LabelFrame(parent, text="Tráfico de Red en Tiempo Real", 
                                     font=('Arial', 12, 'bold'), bg='#1a1a1a', 
                                     fg='#ffffff', bd=2, relief='groove', height=400)
        graph_section.pack(fill=tk.X, pady=(0, 15))
        graph_section.pack_propagate(False)
        
        # Canvas para el gráfico
        canvas_frame = tk.Frame(graph_section, bg='#1a1a1a')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.graph_canvas = tk.Canvas(canvas_frame, bg='#0a0a0a', 
                                     highlightthickness=1, highlightbackground='#333333')
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        
        # SECCIÓN: LOG DE EVENTOS
        log_section = tk.LabelFrame(parent, text="Log de Eventos", 
                                   font=('Arial', 12, 'bold'), bg='#1a1a1a', 
                                   fg='#ffffff', bd=2, relief='groove')
        log_section.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto con scroll para logs
        log_frame = tk.Frame(log_section, bg='#1a1a1a')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=('Consolas', 10),
                                                 bg='#0a0a0a', fg='#ffffff',
                                                 relief=tk.SUNKEN, bd=2,
                                                 wrap=tk.WORD, height=12,
                                                 insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para colores en logs
        self.log_text.tag_configure("normal", foreground="#ffffff")
        self.log_text.tag_configure("alert", foreground="#ff6b6b", font=('Consolas', 10, 'bold'))
        self.log_text.tag_configure("success", foreground="#51cf66")
        self.log_text.tag_configure("warning", foreground="#ffd43b")
        self.log_text.tag_configure("info", foreground="#74c0fc")
    
    def setup_monitoring(self):
        """Configura el sistema de monitoreo"""
        try:
            self.previous_net_io = psutil.net_io_counters()
        except:
            self.previous_net_io = None
        self.monitoring_thread = None
        
        # Agregar mensaje inicial al log
        self.add_log("Monitor de Red iniciado", "info")
        if self.baseline_upload > 0:
            self.add_log(f"Baseline cargado: ↑{self.format_bytes(self.baseline_upload)}/s ↓{self.format_bytes(self.baseline_download)}/s", "success")
        else:
            self.add_log("Baseline no establecido. Ejecuta 'Recalibrar Baseline' primero.", "warning")
    
    def start_monitoring(self):
        """Inicia el monitoreo de red"""
        try:
            self.interval = float(self.interval_var.get())
            self.alert_threshold = float(self.threshold_var.get())
        except ValueError:
            messagebox.showerror("Error", "Los valores de configuración deben ser números válidos")
            return
        
        if self.previous_net_io is None:
            try:
                self.previous_net_io = psutil.net_io_counters()
            except Exception as e:
                messagebox.showerror("Error", f"No se puede acceder a la información de red: {str(e)}")
                return
        
        if self.baseline_upload == 0:
            result = messagebox.askyesno("Baseline no establecido", 
                                       "No hay baseline establecido. ¿Quieres calcularlo automáticamente?")
            if result:
                self.recalibrate_baseline()
            else:
                return
        
        self.monitoring = True
        self.admin_notified = False
        
        # Actualizar UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="● Monitoreando", fg="#28a745")
        
        # Iniciar thread de monitoreo
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.add_log("Monitoreo iniciado", "success")
    
    def stop_monitoring(self):
        """Detiene el monitoreo de red"""
        self.monitoring = False
        
        # Actualizar UI
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Detenido", fg="#dc3545")
        
        self.add_log("Monitoreo detenido", "warning")
    
    def monitoring_loop(self):
        """Loop principal de monitoreo"""
        while self.monitoring:
            try:
                # Obtener datos actuales de red
                current_net_io = psutil.net_io_counters()
                
                if self.previous_net_io:
                    # Calcular velocidades
                    upload_speed = (current_net_io.bytes_sent - self.previous_net_io.bytes_sent) / self.interval
                    download_speed = (current_net_io.bytes_recv - self.previous_net_io.bytes_recv) / self.interval
                    
                    # Evitar valores negativos
                    upload_speed = max(0, upload_speed)
                    download_speed = max(0, download_speed)
                    
                    # Agregar a cola para actualización de UI
                    self.data_queue.put({
                        'upload': upload_speed,
                        'download': download_speed,
                        'timestamp': datetime.now()
                    })
                    
                    # Verificar anomalías
                    self.check_anomalies(upload_speed, download_speed)
                
                # Actualizar datos anteriores
                self.previous_net_io = current_net_io
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.data_queue.put({'error': str(e)})
                break
    
    def check_anomalies(self, upload, download):
        """Verifica si hay anomalías en el tráfico"""
        if self.baseline_upload == 0 or self.baseline_download == 0:
            return
        
        upload_anomaly = upload > self.baseline_upload * self.alert_threshold
        download_anomaly = download > self.baseline_download * self.alert_threshold
        
        if upload_anomaly or download_anomaly:
            if not self.admin_notified:
                alert_msg = f"ANOMALIA DETECTADA:\n"
                alert_msg += f"↑ Subida: {self.format_bytes(upload)}/s (normal: {self.format_bytes(self.baseline_upload)}/s)\n"
                alert_msg += f"↓ Descarga: {self.format_bytes(download)}/s (normal: {self.format_bytes(self.baseline_download)}/s)"
                
                self.data_queue.put({'alert': alert_msg})
                self.admin_notified = True
                
                # Enviar email si está configurado
                if self.email_config['sender']:
                    threading.Thread(target=self.send_alert_email, 
                                   args=(upload, download), daemon=True).start()
        else:
            # Reset si vuelve a la normalidad
            if self.admin_notified:
                self.admin_notified = False
                self.data_queue.put({'alert': "Tráfico vuelto a la normalidad"})
    
    def recalibrate_baseline(self):
        """Recalibra los valores baseline"""
        self.add_log("Iniciando calibración de baseline...", "info")
        
        def calibrate():
            try:
                # Medir durante 10 segundos
                samples = 10
                upload_values = []
                download_values = []
                
                initial_net_io = psutil.net_io_counters()
                
                for i in range(samples):
                    time.sleep(1)
                    current_net_io = psutil.net_io_counters()
                    
                    upload = (current_net_io.bytes_sent - initial_net_io.bytes_sent) / (i + 1)
                    download = (current_net_io.bytes_recv - initial_net_io.bytes_recv) / (i + 1)
                    
                    upload_values.append(max(0, upload))
                    download_values.append(max(0, download))
                    
                    # Actualizar progreso
                    self.data_queue.put({'calibration_progress': (i + 1, samples)})
                
                # Calcular promedios
                self.baseline_upload = sum(upload_values) / len(upload_values)
                self.baseline_download = sum(download_values) / len(download_values)
                
                # Guardar baseline
                self.save_baseline()
                
                self.data_queue.put({'calibration_complete': True})
                
            except Exception as e:
                self.data_queue.put({'calibration_error': str(e)})
        
        # Ejecutar calibración en thread separado
        threading.Thread(target=calibrate, daemon=True).start()
    
    def configure_email(self):
        """Abre ventana de configuración de email"""
        email_window = tk.Toplevel(self.root)
        email_window.title("Configuración de Email")
        email_window.geometry("500x450")
        email_window.configure(bg='#1a1a1a')
        email_window.resizable(False, False)
        email_window.transient(self.root)
        email_window.grab_set()
        
        # Centrar ventana manualmente
        self.center_window(email_window, 500, 450)
        
        # Frame principal
        main_frame = tk.Frame(email_window, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Título
        title_label = tk.Label(main_frame, text="Configuración de Alertas por Email", 
                              font=('Arial', 16, 'bold'), bg='#1a1a1a', fg='#ffffff')
        title_label.pack(pady=(0, 20))
        
        # Campos de configuración
        fields = [
            ("Email emisor:", 'sender'),
            ("Contraseña de app:", 'password'),
            ("Email receptor:", 'receiver'),
            ("Servidor SMTP:", 'smtp_server'),
            ("Puerto SMTP:", 'smtp_port')
        ]
        
        entries = {}
        
        for label_text, key in fields:
            # Frame para cada campo
            field_frame = tk.Frame(main_frame, bg='#1a1a1a')
            field_frame.pack(fill=tk.X, pady=5)
            
            # Label
            label = tk.Label(field_frame, text=label_text, font=('Arial', 11, 'bold'), 
                           bg='#1a1a1a', fg='#ffffff', width=15)
            label.pack(anchor='w', pady=(5, 2))
            
            # Entry
            entry = tk.Entry(field_frame, font=('Arial', 11), bg='#404040', fg='#ffffff',
                           relief=tk.SUNKEN, bd=2, insertbackground='white',
                           show='*' if key == 'password' else None)
            entry.pack(fill=tk.X, pady=(0, 5))
            entry.insert(0, str(self.email_config[key]))
            entries[key] = entry
        
        # Frame de información
        info_frame = tk.Frame(main_frame, bg='#1a1a1a')
        info_frame.pack(fill=tk.X, pady=(15, 10))
        
        info_text = ("Nota: Para Gmail, usa una contraseña de aplicación específica.\n"
                    "Activa la verificación en 2 pasos y genera una contraseña de app.")
        info_label = tk.Label(info_frame, text=info_text, font=('Arial', 9), 
                            bg='#1a1a1a', fg='#888888', justify=tk.LEFT, wraplength=400)
        info_label.pack()
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_config():
            try:
                for key, entry in entries.items():
                    value = entry.get().strip()
                    if key == 'smtp_port':
                        try:
                            value = int(value) if value else 587
                        except ValueError:
                            value = 587
                    self.email_config[key] = value
                
                self.save_config()
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                email_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")
        
        def test_config():
            # Validar campos básicos
            sender = entries['sender'].get().strip()
            password = entries['password'].get().strip()
            receiver = entries['receiver'].get().strip()
            
            if not sender or not password or not receiver:
                messagebox.showwarning("Campos incompletos", 
                                     "Por favor completa al menos el email emisor, contraseña y receptor")
                return
            
            # Guardar temporalmente y probar
            temp_config = self.email_config.copy()
            for key, entry in entries.items():
                value = entry.get().strip()
                if key == 'smtp_port':
                    try:
                        value = int(value) if value else 587
                    except ValueError:
                        value = 587
                temp_config[key] = value
            
            # Probar envío
            def test_send():
                try:
                    message = MIMEMultipart()
                    message["From"] = temp_config['sender']
                    message["To"] = temp_config['receiver']
                    message["Subject"] = "Test - Monitor de Red"
                    
                    body = "Este es un email de prueba del Monitor de Red.\n\nSi recibes este mensaje, la configuración es correcta."
                    message.attach(MIMEText(body, "plain"))
                    
                    server = smtplib.SMTP(temp_config['smtp_server'], temp_config['smtp_port'])
                    server.starttls()
                    server.login(temp_config['sender'], temp_config['password'])
                    server.send_message(message)
                    server.quit()
                    
                    email_window.after(0, lambda: messagebox.showinfo("Test exitoso", 
                                                                     "Email de prueba enviado correctamente"))
                    
                except Exception as e:
                    email_window.after(0, lambda: messagebox.showerror("Test fallido", 
                                                                      f"Error: {str(e)}"))
            
            # Ejecutar test en thread separado
            threading.Thread(target=test_send, daemon=True).start()
            messagebox.showinfo("Test en progreso", "Enviando email de prueba...")
        
        # Botones de acción
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=email_window.destroy,
                              font=('Arial', 11, 'bold'), bg='#6c757d', fg='white',
                              relief=tk.RAISED, padx=20, pady=8, cursor='hand2', bd=2)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = tk.Button(button_frame, text="Guardar", command=save_config,
                            font=('Arial', 11, 'bold'), bg='#28a745', fg='white',
                            relief=tk.RAISED, padx=20, pady=8, cursor='hand2', bd=2)
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        test_btn = tk.Button(button_frame, text="Probar", command=test_config,
                            font=('Arial', 11, 'bold'), bg='#17a2b8', fg='white',
                            relief=tk.RAISED, padx=20, pady=8, cursor='hand2', bd=2)
        test_btn.pack(side=tk.RIGHT)
    
    def test_email(self):
        """Envía un email de prueba"""
        if not self.email_config['sender']:
            messagebox.showwarning("Configuración incompleta", 
                                 "Por favor configura el email primero")
            return
        
        def send_test():
            try:
                message = MIMEMultipart()
                message["From"] = self.email_config['sender']
                message["To"] = self.email_config['receiver']
                message["Subject"] = "Test - Monitor de Red"
                
                body = f"""
Hola,

Este es un email de prueba del Monitor de Red Avanzado.

Configuración actual:
- Servidor SMTP: {self.email_config['smtp_server']}
- Puerto: {self.email_config['smtp_port']}
- Enviado desde: {self.email_config['sender']}

Si recibes este mensaje, la configuración es correcta.

Saludos,
Monitor de Red Avanzado
                """
                
                message.attach(MIMEText(body, "plain"))
                
                server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
                server.starttls()
                server.login(self.email_config['sender'], self.email_config['password'])
                server.send_message(message)
                server.quit()
                
                self.data_queue.put({'email_test': 'success'})
                
            except Exception as e:
                self.data_queue.put({'email_test': f'error: {str(e)}'})
        
        threading.Thread(target=send_test, daemon=True).start()
        self.add_log("Enviando email de prueba...", "info")
    
    def send_alert_email(self, upload, download):
        """Envía email de alerta"""
        try:
            message = MIMEMultipart()
            message["From"] = self.email_config['sender']
            message["To"] = self.email_config['receiver']
            message["Subject"] = "ALERTA - Anomalía en el tráfico de red"
            
            body = f"""
Hola,

Se ha detectado una anomalía en el tráfico de red del servidor.

DETALLES DE LA ANOMALÍA:
- Tráfico de subida: {self.format_bytes(upload)}/s
- Tráfico de descarga: {self.format_bytes(download)}/s

VALORES NORMALES:
- Subida normal: {self.format_bytes(self.baseline_upload)}/s
- Descarga normal: {self.format_bytes(self.baseline_download)}/s

RATIOS:
- Subida: {upload/self.baseline_upload:.1f}x mayor que lo normal
- Descarga: {download/self.baseline_download:.1f}x mayor que lo normal

Hora de detección: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Por favor, revisa la situación lo antes posible.

Saludos,
Monitor de Red Avanzado
            """
            
            message.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            server.send_message(message)
            server.quit()
            
            self.data_queue.put({'email_sent': True})
            
        except Exception as e:
            self.data_queue.put({'email_error': str(e)})
    
    def export_logs(self):
        """Exporta los logs a un archivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar logs como..."
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=== LOGS DEL MONITOR DE RED AVANZADO ===\n")
                    f.write(f"Exportado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.log_text.get(1.0, tk.END))
                
                messagebox.showinfo("Éxito", f"Logs exportados a: {filename}")
                self.add_log(f"Logs exportados a: {filename}", "success")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar logs: {str(e)}")
    
    def clear_logs(self):
        """Limpia el área de logs"""
        result = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar todos los logs?")
        if result:
            self.log_text.delete(1.0, tk.END)
            self.events_log.clear()
            self.add_log("Logs limpiados", "info")
    
    def add_log(self, message, type_tag="normal"):
        """Añade un mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        # Insertar en el área de texto
        self.log_text.insert(tk.END, full_message, type_tag)
        self.log_text.see(tk.END)
        
        # Guardar en lista para exportar
        self.events_log.append((timestamp, message, type_tag))
        
        # Limitar logs a últimos 1000
        if len(self.events_log) > 1000:
            self.events_log = self.events_log[-1000:]
        
        # Actualizar la interfaz
        self.root.update_idletasks()
    
    def update_display(self):
        """Actualiza la interfaz con nuevos datos"""
        # Procesar mensajes de la cola
        try:
            while True:
                data = self.data_queue.get_nowait()
                
                if 'upload' in data and 'download' in data:
                    # Datos normales de monitoreo
                    self.upload_data.append(data['upload'])
                    self.download_data.append(data['download'])
                    self.time_data.append(data['timestamp'])
                    
                    # Actualizar estadísticas
                    self.upload_stat.config(text=f"↑ Subida: {self.format_bytes(data['upload'])}/s")
                    self.download_stat.config(text=f"↓ Descarga: {self.format_bytes(data['download'])}/s")
                    
                elif 'alert' in data:
                    # Alerta detectada
                    self.add_log(data['alert'], "alert")
                    alert_count = len([log for log in self.events_log if log[2] == "alert"])
                    self.alerts_stat.config(text=f"Alertas: {alert_count}")
                    
                elif 'calibration_progress' in data:
                    # Progreso de calibración
                    current, total = data['calibration_progress']
                    self.add_log(f"Calibrando... {current}/{total}", "info")
                    
                elif 'calibration_complete' in data:
                    # Calibración completada
                    self.add_log(f"Baseline establecido: ↑{self.format_bytes(self.baseline_upload)}/s ↓{self.format_bytes(self.baseline_download)}/s", "success")
                    self.baseline_stat.config(text=f"Baseline: ↑{self.format_bytes(self.baseline_upload)}/s ↓{self.format_bytes(self.baseline_download)}/s")
                    
                elif 'calibration_error' in data:
                    self.add_log(f"Error en calibración: {data['calibration_error']}", "alert")
                    
                elif 'email_test' in data:
                    if data['email_test'] == 'success':
                        self.add_log("Email de prueba enviado correctamente", "success")
                    else:
                        self.add_log(f"Error en email de prueba: {data['email_test'][7:]}", "alert")
                        
                elif 'email_sent' in data:
                    self.add_log("Email de alerta enviado", "success")
                    
                elif 'email_error' in data:
                    self.add_log(f"Error enviando email: {data['email_error']}", "alert")
                    
                elif 'error' in data:
                    self.add_log(f"Error de monitoreo: {data['error']}", "alert")
                    self.stop_monitoring()
                    
        except queue.Empty:
            pass
        
        # Actualizar gráfico
        self.update_graph()
        
        # Programar próxima actualización
        self.root.after(1000, self.update_display)
    
    def update_graph(self):
        """Actualiza el gráfico en tiempo real"""
        self.graph_canvas.delete("all")
        
        canvas_width = self.graph_canvas.winfo_width()
        canvas_height = self.graph_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        if not self.upload_data or not self.download_data:
            # Mostrar mensaje cuando no hay datos
            self.graph_canvas.create_text(canvas_width//2, canvas_height//2, 
                                        text="Esperando datos de monitoreo...",
                                        fill="#888888", font=('Arial', 14))
            return
        
        # Márgenes
        margin_left = 80
        margin_right = 20
        margin_top = 20
        margin_bottom = 40
        
        graph_width = canvas_width - margin_left - margin_right
        graph_height = canvas_height - margin_top - margin_bottom
        
        if graph_width <= 0 or graph_height <= 0:
            return
        
        # Encontrar valores máximo y mínimo
        all_values = list(self.upload_data) + list(self.download_data)
        if all_values:
            max_value = max(all_values)
            min_value = min(all_values)
            
            if max_value == min_value:
                max_value += 1000  # Agregar un poco de rango
            
            # Dibujar líneas de fondo (grid)
            for i in range(5):
                y = margin_top + (graph_height / 4) * i
                self.graph_canvas.create_line(margin_left, y, canvas_width - margin_right, y,
                                            fill="#333333", width=1)
            
            # Dibujar líneas verticales
            for i in range(6):
                x = margin_left + (graph_width / 5) * i
                self.graph_canvas.create_line(x, margin_top, x, canvas_height - margin_bottom,
                                            fill="#333333", width=1)
            
            # Dibujar labels del eje Y
            for i in range(5):
                value = max_value - ((max_value - min_value) / 4) * i
                y = margin_top + (graph_height / 4) * i
                self.graph_canvas.create_text(margin_left - 10, y, 
                                            text=self.format_bytes(value, short=True),
                                            fill="#888888", font=('Arial', 9), anchor='e')
            
            # Dibujar datos de subida (verde)
            if len(self.upload_data) > 1:
                points = []
                for i, value in enumerate(self.upload_data):
                    x = margin_left + (graph_width / (len(self.upload_data) - 1)) * i
                    y_ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
                    y = margin_top + graph_height - (y_ratio * graph_height)
                    points.extend([x, y])
                
                if len(points) >= 4:
                    self.graph_canvas.create_line(points, fill="#00ff88", width=2, smooth=True)
            
            # Dibujar datos de descarga (azul)
            if len(self.download_data) > 1:
                points = []
                for i, value in enumerate(self.download_data):
                    x = margin_left + (graph_width / (len(self.download_data) - 1)) * i
                    y_ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
                    y = margin_top + graph_height - (y_ratio * graph_height)
                    points.extend([x, y])
                
                if len(points) >= 4:
                    self.graph_canvas.create_line(points, fill="#007acc", width=2, smooth=True)
            
            # Líneas de baseline si están establecidas
            if self.baseline_upload > 0 and min_value <= self.baseline_upload <= max_value:
                y_ratio = (self.baseline_upload - min_value) / (max_value - min_value)
                y_up = margin_top + graph_height - (y_ratio * graph_height)
                self.graph_canvas.create_line(margin_left, y_up, canvas_width - margin_right, y_up,
                                            fill="#00ff88", width=1, dash=(5, 5))
                
            if self.baseline_download > 0 and min_value <= self.baseline_download <= max_value:
                y_ratio = (self.baseline_download - min_value) / (max_value - min_value)
                y_down = margin_top + graph_height - (y_ratio * graph_height)
                self.graph_canvas.create_line(margin_left, y_down, canvas_width - margin_right, y_down,
                                            fill="#007acc", width=1, dash=(5, 5))
        
        # Leyenda
        legend_y = canvas_height - 20
        self.graph_canvas.create_text(margin_left + 20, legend_y, 
                                    text="↑ Subida", fill="#00ff88", font=('Arial', 10), anchor='w')
        self.graph_canvas.create_text(margin_left + 120, legend_y, 
                                    text="↓ Descarga", fill="#007acc", font=('Arial', 10), anchor='w')
        
        if self.baseline_upload > 0:
            self.graph_canvas.create_text(margin_left + 240, legend_y, 
                                        text="--- Baseline", fill="#888888", font=('Arial', 10), anchor='w')
    
    def format_bytes(self, bytes_value, short=False):
        """Formatea bytes a unidades legibles"""
        if bytes_value == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while bytes_value >= 1024 and unit_index < len(units) - 1:
            bytes_value /= 1024
            unit_index += 1
        
        if short and bytes_value >= 100:
            return f"{bytes_value:.0f}{units[unit_index]}"
        elif short:
            return f"{bytes_value:.1f}{units[unit_index]}"
        else:
            return f"{bytes_value:.2f} {units[unit_index]}"
    
    def save_config(self):
        """Guarda la configuración en archivo"""
        config = {
            'email_config': self.email_config,
            'interval': self.interval,
            'alert_threshold': self.alert_threshold
        }
        
        try:
            with open('network_monitor_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.add_log(f"Error guardando configuración: {str(e)}", "alert")
    
    def load_config(self):
        """Carga la configuración desde archivo"""
        try:
            if os.path.exists('network_monitor_config.json'):
                with open('network_monitor_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.email_config.update(config.get('email_config', {}))
                self.interval = config.get('interval', 1.0)
                self.alert_threshold = config.get('alert_threshold', 15.0)
                
        except Exception as e:
            self.add_log(f"Error cargando configuración: {str(e)}", "alert")
    
    def save_baseline(self):
        """Guarda los valores baseline en archivo"""
        baseline_data = {
            'upload': self.baseline_upload,
            'download': self.baseline_download,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open('network_baseline.json', 'w', encoding='utf-8') as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.add_log(f"Error guardando baseline: {str(e)}", "alert")
    
    def load_baseline(self):
        """Carga los valores baseline desde archivo"""
        try:
            if os.path.exists('network_baseline.json'):
                with open('network_baseline.json', 'r', encoding='utf-8') as f:
                    baseline_data = json.load(f)
                
                self.baseline_upload = baseline_data.get('upload', 0)
                self.baseline_download = baseline_data.get('download', 0)
                
        except Exception as e:
            self.add_log(f"Error cargando baseline: {str(e)}", "alert")
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if self.monitoring:
            self.stop_monitoring()
        
        # Guardar configuración
        self.save_config()
        
        self.root.destroy()

def main():
    """Función principal"""
    # Verificar dependencias
    try:
        import psutil
    except ImportError:
        print("Instalando psutil...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "psutil"])
            import psutil
        except Exception as e:
            print(f"Error instalando psutil: {e}")
            print("Por favor instala psutil manualmente: pip install psutil")
            return
    
    # Crear y ejecutar la aplicación
    try:
        app = NetworkMonitorGUI()
        app.run()
    except Exception as e:
        print(f"Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()