import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import json
import os
import subprocess
from datetime import datetime
import queue

class ChatServer:
    def __init__(self):
        self.config = self.load_config()
        self.running = False
        self.clients = {}  # {addr: (conn, username)}
        self.message_queue = queue.Queue()
        
        # Crear la interfaz gráfica
        self.setup_gui()
        
        # Iniciar el hilo para procesar mensajes de la cola
        self.start_message_processor()
        
    def load_config(self):
        """Carga configuración del servidor"""
        default_config = {
            "host": "0.0.0.0",
            "port": 3000,
            "max_connections": 20
        }
        
        try:
            with open('server_config.json', 'r') as f:
                config = json.load(f)
            return {**default_config, **config}
        except:
            return default_config
    
    def setup_gui(self):
        """Diseño limpio para el servidor"""
        self.root = tk.Tk()
        self.root.title("🌐 Servidor de Chat - Radmin VPN")
        self.root.geometry("650x800")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(True, True)
        
        # Container principal
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # HEADER - Barra superior
        header = tk.Frame(main_container, bg='#2d2d2d', height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#2d2d2d')
        header_content.pack(expand=True, fill='both', padx=25, pady=20)
        
        # Título y status
        title_frame = tk.Frame(header_content, bg='#2d2d2d')
        title_frame.pack(side=tk.LEFT)
        
        title = tk.Label(title_frame, text="🌐 Servidor de Chat", font=('Arial', 16, 'bold'), 
                        fg='#ffffff', bg='#2d2d2d')
        title.pack(anchor='w')
        
        self.status_label = tk.Label(title_frame, text="● Detenido", font=('Arial', 10), 
                                    fg='#ff4444', bg='#2d2d2d')
        self.status_label.pack(anchor='w')
        
        # Controles del servidor
        controls_frame = tk.Frame(header_content, bg='#2d2d2d')
        controls_frame.pack(side=tk.RIGHT)
        
        # Configuración
        config_row = tk.Frame(controls_frame, bg='#2d2d2d')
        config_row.pack(anchor='e', pady=(0, 12))
        
        tk.Label(config_row, text="Host:", font=('Arial', 11, 'bold'), 
                fg='#bdc3c7', bg='#2d2d2d').pack(side=tk.LEFT, padx=(0, 8))
        
        self.host_var = tk.StringVar(value="0.0.0.0")
        host_entry = tk.Entry(config_row, textvariable=self.host_var, 
                             font=('Arial', 11), bg='#404040', fg='#ffffff', 
                             relief=tk.FLAT, width=12, insertbackground='#ffffff',
                             bd=2)
        host_entry.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Label(config_row, text="Puerto:", font=('Arial', 11, 'bold'), 
                fg='#bdc3c7', bg='#2d2d2d').pack(side=tk.LEFT, padx=(0, 8))
        
        self.port_var = tk.StringVar(value=str(self.config['port']))
        port_entry = tk.Entry(config_row, textvariable=self.port_var, 
                             font=('Arial', 11), bg='#404040', fg='#ffffff', 
                             relief=tk.FLAT, width=10, insertbackground='#ffffff',
                             bd=2)
        port_entry.pack(side=tk.LEFT, padx=(0, 0))
        
        # Botones de control
        button_row = tk.Frame(controls_frame, bg='#2d2d2d')
        button_row.pack(anchor='e')
        
        self.start_btn = tk.Button(button_row, text="▶ INICIAR", 
                                  command=self.start_server, font=('Arial', 12, 'bold'),
                                  bg='#28a745', fg='white', relief=tk.FLAT, 
                                  padx=35, pady=15, cursor='hand2',
                                  activebackground='#218838', width=12)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        self.stop_btn = tk.Button(button_row, text="⏹ DETENER", 
                                 command=self.stop_server, font=('Arial', 12, 'bold'),
                                 bg='#dc3545', fg='white', relief=tk.FLAT, 
                                 padx=35, pady=15, cursor='hand2', state=tk.DISABLED,
                                 activebackground='#c82333', width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        # Botón para gestionar clientes
        self.manage_btn = tk.Button(button_row, text="👥 CLIENTES", 
                                   command=self.open_client_manager, font=('Arial', 12, 'bold'),
                                   bg='#6f42c1', fg='white', relief=tk.FLAT, 
                                   padx=35, pady=15, cursor='hand2', state=tk.DISABLED,
                                   activebackground='#5a2d91', width=12)
        self.manage_btn.pack(side=tk.LEFT)
        
        # PANEL RADMIN VPN - Información útil
        radmin_panel = tk.Frame(main_container, bg='#1a4d3a', height=120)
        radmin_panel.pack(fill=tk.X)
        radmin_panel.pack_propagate(False)
        
        radmin_content = tk.Frame(radmin_panel, bg='#1a4d3a')
        radmin_content.pack(expand=True, fill='both', padx=20, pady=15)
        
        # Título del panel
        radmin_title = tk.Label(radmin_content, text="🌐 Radmin VPN - Conexión Remota", 
                               font=('Arial', 12, 'bold'), fg='#ffffff', bg='#1a4d3a')
        radmin_title.pack(anchor='w')
        
        # Instrucciones
        instructions = tk.Label(radmin_content, 
                               text="• Crea una red en Radmin VPN  • Comparte: Nombre de red + Password  • Tu IP Radmin será visible para conectar", 
                               font=('Arial', 9), fg='#a8e6a8', bg='#1a4d3a', wraplength=600)
        instructions.pack(anchor='w', pady=(5, 8))
        
        # Fila de información
        info_row = tk.Frame(radmin_content, bg='#1a4d3a')
        info_row.pack(fill=tk.X)
        
        # IP Local
        local_ip = self.get_local_ip()
        tk.Label(info_row, text="🏠 Red local:", font=('Arial', 10, 'bold'), 
                fg='#ffffff', bg='#1a4d3a').pack(side=tk.LEFT)
        
        self.local_ip_display = tk.Entry(info_row, font=('Arial', 10), bg='#2d4a2d', 
                                        fg='#90ee90', relief=tk.FLAT, state='readonly', 
                                        bd=2, width=20)
        self.local_ip_display.pack(side=tk.LEFT, padx=(8, 10))
        
        # Botón copiar IP
        self.copy_ip_btn = tk.Button(info_row, text="📋 Copiar", command=self.copy_local_ip,
                                    font=('Arial', 9, 'bold'), bg='#28a745', fg='white', 
                                    relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        self.copy_ip_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Información del puerto
        tk.Label(info_row, text="Puerto:", font=('Arial', 10, 'bold'), 
                fg='#ffffff', bg='#1a4d3a').pack(side=tk.LEFT)
        
        self.port_display = tk.Label(info_row, text="3000", font=('Arial', 10, 'bold'), 
                                    fg='#90ee90', bg='#1a4d3a')
        self.port_display.pack(side=tk.LEFT, padx=(8, 0))
        
        # Botón info Radmin
        self.radmin_info_btn = tk.Button(info_row, text="ℹ️ Ayuda Radmin", 
                                        command=self.show_radmin_help,
                                        font=('Arial', 9, 'bold'), bg='#17a2b8', fg='white', 
                                        relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        self.radmin_info_btn.pack(side=tk.RIGHT)
        
        # STATS BAR
        stats_bar = tk.Frame(main_container, bg='#2d2d2d', height=50)
        stats_bar.pack(fill=tk.X)
        stats_bar.pack_propagate(False)
        
        stats_content = tk.Frame(stats_bar, bg='#2d2d2d')
        stats_content.pack(expand=True, fill='both', padx=20, pady=12)
        
        # Estadísticas
        self.clients_stat = tk.Label(stats_content, text="0 clientes", font=('Arial', 11), 
                                    fg='#ffffff', bg='#2d2d2d')
        self.clients_stat.pack(side=tk.LEFT)
        
        self.messages_stat = tk.Label(stats_content, text="0 mensajes", font=('Arial', 11), 
                                     fg='#ffffff', bg='#2d2d2d')
        self.messages_stat.pack(side=tk.LEFT, padx=(30, 0))
        
        self.uptime_stat = tk.Label(stats_content, text="00:00:00", font=('Arial', 11), 
                                   fg='#ffffff', bg='#2d2d2d')
        self.uptime_stat.pack(side=tk.RIGHT)
        
        # CONTENT AREA
        content_area = tk.Frame(main_container, bg='#1e1e1e')
        content_area.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Panel izquierdo - Clientes conectados
        left_panel = tk.Frame(content_area, bg='#1e1e1e', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 10), pady=20)
        left_panel.pack_propagate(False)
        
        clients_title = tk.Label(left_panel, text="Usuarios Conectados", font=('Arial', 12, 'bold'), 
                                fg='#ffffff', bg='#1e1e1e')
        clients_title.pack(anchor='w', pady=(0, 10))
        
        self.clients_listbox = tk.Listbox(left_panel, font=('Arial', 10),
                                         bg='#2d2d2d', fg='#e0e0e0', relief=tk.FLAT,
                                         selectbackground='#404040', bd=0,
                                         highlightthickness=0, activestyle='none')
        self.clients_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Panel derecho - Log de actividad
        right_panel = tk.Frame(content_area, bg='#1e1e1e')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=20)
        
        log_title = tk.Label(right_panel, text="Actividad del Servidor", font=('Arial', 12, 'bold'), 
                            fg='#ffffff', bg='#1e1e1e')
        log_title.pack(anchor='w', pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(right_panel, font=('Consolas', 9),
                                                 bg='#2d2d2d', fg='#e0e0e0', 
                                                 relief=tk.FLAT, bd=0, wrap=tk.WORD,
                                                 insertbackground='#ffffff',
                                                 selectbackground='#404040',
                                                 highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Variables para estadísticas
        self.message_count = 0
        self.start_time = None
        
        # Configurar colores del log
        self.log_text.tag_configure("success", foreground="#4ecdc4")
        self.log_text.tag_configure("error", foreground="#ff6b6b")
        self.log_text.tag_configure("warning", foreground="#ffbe76")
        self.log_text.tag_configure("info", foreground="#74b9ff")
        self.log_text.tag_configure("message", foreground="#a8e6cf")
        self.log_text.tag_configure("radmin", foreground="#90ee90")
        
        # Mensaje inicial
        self.add_log_message("🌐 Servidor de Chat listo", "info")
        self.add_log_message("💡 Usa Radmin VPN para conexiones remotas", "radmin")
        
        # Actualizar IP local
        self.update_local_ip()
        
    def get_local_ip(self):
        """Obtiene la IP local"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def update_local_ip(self):
        """Actualiza la IP local mostrada"""
        local_ip = self.get_local_ip()
        port = self.port_var.get()
        
        self.local_ip_display.config(state='normal')
        self.local_ip_display.delete(0, tk.END)
        self.local_ip_display.insert(0, f"{local_ip}:{port}")
        self.local_ip_display.config(state='readonly')
        
        self.port_display.config(text=port)
    
    def copy_local_ip(self):
        """Copia la IP local al portapapeles"""
        ip_info = self.local_ip_display.get()
        if ip_info:
            self.root.clipboard_clear()
            self.root.clipboard_append(ip_info)
            
            # Confirmación visual
            original_text = self.copy_ip_btn.cget("text")
            self.copy_ip_btn.config(text="✅ Copiado")
            self.root.after(1500, lambda: self.copy_ip_btn.config(text=original_text))
            
            self.add_log_message("📋 IP local copiada al portapapeles", "info")
    
    def show_radmin_help(self):
        """Muestra ayuda para Radmin VPN"""
        help_window = tk.Toplevel(self.root)
        help_window.title("🌐 Guía Radmin VPN")
        help_window.geometry("500x450")
        help_window.configure(bg='#2d2d2d')
        help_window.resizable(False, False)
        
        # Centrar ventana
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Contenido
        content = tk.Frame(help_window, bg='#2d2d2d')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(content, text="🌐 Guía para usar Radmin VPN", 
                        font=('Arial', 14, 'bold'), fg='#ffffff', bg='#2d2d2d')
        title.pack(pady=(0, 15))
        
        help_text = tk.Text(content, font=('Arial', 10), bg='#1e1e1e', fg='#e0e0e0',
                           relief=tk.FLAT, bd=0, wrap=tk.WORD, height=20)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        local_ip = self.get_local_ip()
        port = self.port_var.get()
        
        instructions = f"""📥 PASO 1: DESCARGA
• Ambos descargan Radmin VPN: https://www.radmin-vpn.com/
• Instalación gratuita, sin registro requerido

🌐 PASO 2: CREAR RED (TÚ)
• Abre Radmin VPN
• Click "Crear red"
• Nombre: Chat-{local_ip.split('.')[-1]} (o cualquier nombre)
• Password: 123456 (o tu password)

👥 PASO 3: UNIRSE A RED (TU AMIGO)
• Abre Radmin VPN
• Click "Unirse a red"
• Introduce el nombre y password de tu red
• Espera a conectarse

🔗 PASO 4: OBTENER IP RADMIN
• En Radmin VPN verás las IPs de los conectados
• Tu IP será algo como: 25.123.45.67
• Comparte esta IP con tu amigo

💻 PASO 5: CONFIGURAR CLIENTE
Tu amigo configura su cliente:
• Servidor: 25.123.45.67 (tu IP de Radmin)
• Puerto: {port}
• Usuario: [su nombre]

✅ VENTAJAS RADMIN VPN:
• Totalmente gratis sin límites
• Fácil configuración
• Excelente velocidad
• Funciona con cualquier aplicación
• Sin problemas de firewall

⚠️ IMPORTANTE:
• Tu servidor debe estar en 0.0.0.0:{port}
• Mantén Radmin VPN ejecutándose
• Comparte: Nombre de red + Password + Tu IP Radmin"""
        
        help_text.insert(tk.END, instructions)
        help_text.config(state=tk.DISABLED)
        
        # Botón cerrar
        tk.Button(content, text="✅ Entendido", command=help_window.destroy,
                 font=('Arial', 11, 'bold'), bg='#28a745', fg='white', 
                 relief=tk.FLAT, padx=20, pady=8, cursor='hand2').pack(pady=15)
    
    def start_message_processor(self):
        """Procesador de mensajes para la GUI"""
        def process_messages():
            try:
                while True:
                    message_type, message = self.message_queue.get(timeout=0.1)
                    if message_type == "log":
                        self.add_log_message(message[0], message[1])
                    elif message_type == "client_update":
                        self.update_client_list()
                    elif message_type == "stats":
                        self.update_stats()
                    self.message_queue.task_done()
            except queue.Empty:
                pass
            
            self.root.after(100, process_messages)
        
        self.root.after(100, process_messages)
    
    def add_log_message(self, message, tag="info"):
        """Añade mensaje al log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", "info")
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        
        # Limitar tamaño del log
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 500:
            self.log_text.delete('1.0', '50.0')
    
    def update_client_list(self):
        """Actualiza la lista de clientes"""
        self.clients_listbox.delete(0, tk.END)
        for addr, (conn, username) in self.clients.items():
            self.clients_listbox.insert(tk.END, f"🟢 {username}")
            self.clients_listbox.insert(tk.END, f"   {addr[0]}:{addr[1]}")
    
    def update_stats(self):
        """Actualiza estadísticas"""
        client_count = len(self.clients)
        
        if self.start_time:
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split('.')[0]
        else:
            uptime_str = "00:00:00"
        
        self.clients_stat.config(text=f"{client_count} clientes")
        self.messages_stat.config(text=f"{self.message_count} mensajes")
        self.uptime_stat.config(text=uptime_str)
    
    def start_server(self):
        """Inicia el servidor"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get())
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(self.config['max_connections'])
            
            self.running = True
            self.start_time = datetime.now()
            
            # Actualizar interfaz
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.manage_btn.config(state=tk.NORMAL)
            self.status_label.config(text="● Ejecutándose", fg='#28a745')
            
            # Actualizar IP
            self.update_local_ip()
            
            # Log de inicio
            local_ip = self.get_local_ip()
            self.add_log_message(f"🚀 Servidor iniciado en {host}:{port}", "success")
            self.add_log_message(f"🏠 Acceso local: {local_ip}:{port}", "info")
            self.add_log_message("🌐 Para acceso remoto: Usar Radmin VPN", "radmin")
            
            # Iniciar hilo para aceptar conexiones
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar servidor: {str(e)}")
            self.add_log_message(f"❌ Error: {str(e)}", "error")
    
    def stop_server(self):
        """Detiene el servidor"""
        self.running = False
        
        # Cerrar conexiones
        for addr, (conn, username) in list(self.clients.items()):
            try:
                conn.close()
            except:
                pass
        self.clients.clear()
        
        # Cerrar socket del servidor
        try:
            self.server_socket.close()
        except:
            pass
        
        # Actualizar interfaz
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.manage_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Detenido", fg='#ff4444')
        
        self.add_log_message("⏹ Servidor detenido", "warning")
        self.message_queue.put(("client_update", None))
        
        self.start_time = None
        self.message_queue.put(("stats", None))
    
    def accept_connections(self):
        """Acepta nuevas conexiones"""
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                
                # Timeout para handshake
                conn.settimeout(30.0)
                
                try:
                    self.message_queue.put(("log", (f"🔗 Nueva conexión desde {addr[0]}:{addr[1]}", "info")))
                    
                    conn.send("NOMBRE_USUARIO".encode('utf-8'))
                    username_data = conn.recv(1024).decode('utf-8').strip()
                    username = username_data if username_data and len(username_data) > 0 else f"Usuario_{addr[1]}"
                    
                    # Añadir cliente
                    self.clients[addr] = (conn, username)
                    
                    self.message_queue.put(("log", (f"✅ {username} conectado exitosamente ({addr[0]})", "success")))
                    self.message_queue.put(("client_update", None))
                    
                    # Notificar a todos los clientes
                    join_message = f"🟢 {username} se ha unido al chat"
                    self.broadcast_message(join_message)
                    
                    # Iniciar hilo para manejar el cliente
                    client_thread = threading.Thread(target=self.handle_client, 
                                                   args=(conn, addr, username), daemon=True)
                    client_thread.start()
                    
                except socket.timeout:
                    self.message_queue.put(("log", (f"⏰ Timeout en handshake con {addr[0]}", "warning")))
                    try:
                        conn.close()
                    except:
                        pass
                except Exception as handshake_error:
                    self.message_queue.put(("log", (f"❌ Error en handshake con {addr[0]}: {handshake_error}", "error")))
                    try:
                        conn.close()
                    except:
                        pass
                    
            except socket.error as e:
                if self.running:
                    self.message_queue.put(("log", (f"❌ Error aceptando conexión: {e}", "error")))
                break
    
    def handle_client(self, conn, addr, username):
        """Maneja la comunicación con un cliente"""
        try:
            conn.settimeout(60.0)  # Timeout largo para estabilidad
            
            while self.running:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    try:
                        message = data.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        continue
                    
                    if message:
                        # ✅ NUEVO: Manejar mensajes de "escribiendo..."
                        if message.startswith("TYPING:"):
                            # Reenviar señal de typing a otros clientes
                            self.broadcast_message(message, exclude_addr=addr)
                            self.message_queue.put(("log", (f"📝 {username} está escribiendo...", "info")))
                            continue
                        elif message.startswith("STOP_TYPING:"):
                            # Reenviar señal de stop typing a otros clientes
                            self.broadcast_message(message, exclude_addr=addr)
                            continue
                        else:
                            # Mensaje normal del chat
                            self.message_count += 1
                            
                            # Broadcast del mensaje
                            broadcast_msg = f"{username}: {message}"
                            self.broadcast_message(broadcast_msg, exclude_addr=addr)
                            
                            self.message_queue.put(("log", (f"💬 {username}: {message}", "message")))
                            self.message_queue.put(("stats", None))
                            
                            # Confirmación
                            try:
                                conn.send("MSG_OK".encode('utf-8'))
                            except:
                                break
                            
                except socket.timeout:
                    continue
                except (ConnectionResetError, ConnectionAbortedError):
                    break
                except Exception:
                    break
                    
        except Exception:
            pass
        finally:
            # Limpiar cliente desconectado
            if addr in self.clients:
                username = self.clients[addr][1]
                del self.clients[addr]
                
                # Notificar desconexión
                leave_message = f"🔴 {username} ha salido del chat"
                self.broadcast_message(leave_message)
                
                self.message_queue.put(("log", (f"👋 {username} desconectado", "warning")))
                self.message_queue.put(("client_update", None))
                self.message_queue.put(("stats", None))
            
            try:
                conn.close()
            except:
                pass
    
    def broadcast_message(self, message, exclude_addr=None):
        """Envía mensaje a todos los clientes"""
        disconnected = []
        for addr, (conn, username) in self.clients.items():
            if addr == exclude_addr:
                continue
            try:
                # ✅ NUEVO: Enviar señales de typing directamente, otros mensajes con BROADCAST:
                if message.startswith("TYPING:") or message.startswith("STOP_TYPING:"):
                    conn.send(message.encode('utf-8'))
                else:
                    conn.send(f"BROADCAST:{message}".encode('utf-8'))
            except:
                disconnected.append(addr)
        
        # Limpiar conexiones muertas
        for addr in disconnected:
            if addr in self.clients:
                del self.clients[addr]
        
        if disconnected:
            self.message_queue.put(("client_update", None))
    
    def open_client_manager(self):
        """Abre ventana para gestionar clientes conectados"""
        if not self.clients:
            messagebox.showinfo("Sin Clientes", "No hay clientes conectados actualmente")
            return
        
        # Crear ventana de gestión
        manager_window = tk.Toplevel(self.root)
        manager_window.title("👥 Gestión de Clientes")
        manager_window.geometry("450x400")
        manager_window.configure(bg='#1e1e1e')
        manager_window.resizable(False, False)
        
        # Centrar ventana
        manager_window.transient(self.root)
        manager_window.grab_set()
        
        # Header
        header = tk.Frame(manager_window, bg='#2d2d2d', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#2d2d2d')
        header_content.pack(expand=True, fill='both', padx=20, pady=15)
        
        title = tk.Label(header_content, text="👥 Gestión de Clientes Conectados", 
                        font=('Arial', 14, 'bold'), fg='#ffffff', bg='#2d2d2d')
        title.pack(side=tk.LEFT)
        
        client_count = tk.Label(header_content, text=f"{len(self.clients)} conectados", 
                               font=('Arial', 10), fg='#bdc3c7', bg='#2d2d2d')
        client_count.pack(side=tk.RIGHT)
        
        # Lista de clientes
        list_frame = tk.Frame(manager_window, bg='#1e1e1e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        listbox_frame = tk.Frame(list_frame, bg='#1e1e1e')
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, bg='#404040', troughcolor='#2d2d2d')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        client_listbox = tk.Listbox(listbox_frame, font=('Arial', 11),
                                   bg='#2d2d2d', fg='#e0e0e0', relief=tk.FLAT,
                                   selectbackground='#6f42c1', bd=0,
                                   highlightthickness=0, activestyle='none',
                                   yscrollcommand=scrollbar.set)
        client_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=client_listbox.yview)
        
        # Poblar lista
        client_data = {}
        for i, (addr, (conn, username)) in enumerate(self.clients.items()):
            display_text = f"🔗 {username} ({addr[0]}:{addr[1]})"
            client_listbox.insert(tk.END, display_text)
            client_data[i] = addr
        
        # Botones de acción
        action_frame = tk.Frame(manager_window, bg='#1e1e1e', height=80)
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        action_frame.pack_propagate(False)
        
        button_container = tk.Frame(action_frame, bg='#1e1e1e')
        button_container.pack(expand=True, fill='both', pady=15)
        
        # Botón expulsar seleccionado
        def kick_selected():
            selection = client_listbox.curselection()
            if not selection:
                messagebox.showwarning("Sin Selección", "Selecciona un cliente para expulsar")
                return
            
            index = selection[0]
            if index in client_data:
                addr = client_data[index]
                if addr in self.clients:
                    username = self.clients[addr][1]
                    result = messagebox.askyesno("Confirmar Expulsión", 
                                               f"¿Expulsar a '{username}'?")
                    if result:
                        self.kick_client(addr)
                        manager_window.destroy()
        
        kick_btn = tk.Button(button_container, text="🚫 Expulsar Seleccionado", 
                            command=kick_selected, font=('Arial', 11, 'bold'),
                            bg='#e74c3c', fg='white', relief=tk.FLAT, 
                            padx=25, pady=12, cursor='hand2')
        kick_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botón expulsar todos
        def kick_all():
            if self.clients:
                result = messagebox.askyesno("Confirmar Expulsión Masiva", 
                                           f"¿Expulsar a TODOS los {len(self.clients)} clientes?")
                if result:
                    self.kick_all_clients()
                    manager_window.destroy()
        
        kick_all_btn = tk.Button(button_container, text="💥 Expulsar Todos", 
                                command=kick_all, font=('Arial', 11, 'bold'),
                                bg='#dc3545', fg='white', relief=tk.FLAT, 
                                padx=25, pady=12, cursor='hand2')
        kick_all_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botón cerrar
        close_btn = tk.Button(button_container, text="❌ Cerrar", 
                             command=manager_window.destroy, font=('Arial', 11, 'bold'),
                             bg='#6c757d', fg='white', relief=tk.FLAT, 
                             padx=25, pady=12, cursor='hand2')
        close_btn.pack(side=tk.RIGHT)
    
    def kick_client(self, addr):
        """Expulsa un cliente específico"""
        if addr in self.clients:
            conn, username = self.clients[addr]
            
            try:
                conn.send("KICKED:Has sido expulsado del servidor".encode('utf-8'))
                conn.close()
            except:
                pass
            
            del self.clients[addr]
            
            kick_message = f"🔨 {username} ha sido expulsado del servidor"
            self.broadcast_message(kick_message)
            
            self.message_queue.put(("log", (f"🔨 EXPULSADO: {username} ({addr[0]})", "warning")))
            self.message_queue.put(("client_update", None))
            self.message_queue.put(("stats", None))
    
    def kick_all_clients(self):
        """Expulsa a todos los clientes conectados"""
        kicked_users = []
        
        for addr, (conn, username) in list(self.clients.items()):
            try:
                conn.send("KICKED:Servidor cerrado por administrador".encode('utf-8'))
                conn.close()
            except:
                pass
            kicked_users.append(username)
        
        self.clients.clear()
        
        users_list = ", ".join(kicked_users)
        self.message_queue.put(("log", (f"💥 EXPULSIÓN MASIVA: {users_list}", "warning")))
        self.message_queue.put(("client_update", None))
        self.message_queue.put(("stats", None))
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Actualizar estadísticas periódicamente
        def update_stats_periodic():
            self.message_queue.put(("stats", None))
            self.root.after(1000, update_stats_periodic)
        
        self.root.after(1000, update_stats_periodic)
        self.root.mainloop()
    
    def on_closing(self):
        """Cierre de la aplicación"""
        if self.running:
            self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    server = ChatServer()
    server.run()