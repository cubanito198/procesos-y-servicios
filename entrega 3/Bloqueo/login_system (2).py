import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import time
import bcrypt
import threading
from datetime import datetime
import os

class MinimalLoginSystem:
    def __init__(self):
        self.setup_database()
        self.current_mode = "login"  # "login" o "register"
        
        # Configuración de seguridad
        self.MAX_ATTEMPTS = 3
        self.BLOCK_TIME = 300  # 5 minutos
        
        # Crear interfaz gráfica
        self.setup_gui()
        
    def setup_database(self):
        """Configura la base de datos SQLite"""
        self.db_name = "secure_users.db"
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY,
                          username TEXT UNIQUE,
                          password_hash TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          last_login TIMESTAMP,
                          failed_attempts INTEGER DEFAULT 0,
                          blocked_until INTEGER DEFAULT 0
                          )''')
        
        # Tabla de intentos de login
        cursor.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
                          id INTEGER PRIMARY KEY,
                          username TEXT,
                          ip_address TEXT,
                          attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          success INTEGER DEFAULT 0
                          )''')
        
        conn.commit()
        conn.close()
    
    def setup_gui(self):
        """Diseño minimalista y moderno"""
        self.root = tk.Tk()
        self.root.title("🔐 Secure Access")
        self.root.geometry("450x700")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(True, True)  # AHORA SÍ se puede redimensionar
        
        # Centrar ventana en pantalla
        self.root.eval('tk::PlaceWindow . center')
        
        # Container principal
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)  # Menos padding vertical
        
        # HEADER - Logo y título
        header_frame = tk.Frame(main_container, bg='#1e1e1e')
        header_frame.pack(fill=tk.X, pady=(0, 20))  # Menos espacio abajo
        
        # Icono de seguridad
        security_icon = tk.Label(header_frame, text="🔐", font=('Arial', 36), 
                                bg='#1e1e1e', fg='#007acc')
        security_icon.pack()
        
        self.title_label = tk.Label(header_frame, text="Iniciar Sesión", 
                                   font=('Arial', 20, 'bold'), 
                                   bg='#1e1e1e', fg='#ffffff')
        self.title_label.pack(pady=(8, 0))
        
        self.subtitle_label = tk.Label(header_frame, text="Acceso seguro al sistema", 
                                      font=('Arial', 11), 
                                      bg='#1e1e1e', fg='#888888')
        self.subtitle_label.pack(pady=(5, 0))
        
        # FORM CONTAINER
        form_container = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT)
        form_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))  # Menos espacio abajo
        
        # Padding interno del formulario
        form_content = tk.Frame(form_container, bg='#2d2d2d')
        form_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)  # Menos padding
        
        # Campo Usuario
        tk.Label(form_content, text="Usuario", font=('Arial', 12, 'bold'), 
                bg='#2d2d2d', fg='#ffffff').pack(anchor='w', pady=(0, 8))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(form_content, textvariable=self.username_var, 
                                      font=('Arial', 12), bg='#404040', fg='#ffffff',
                                      relief=tk.FLAT, bd=0, insertbackground='#ffffff')
        self.username_entry.pack(fill=tk.X, ipady=10, pady=(0, 15))
        
        # Campo Contraseña
        tk.Label(form_content, text="Contraseña", font=('Arial', 12, 'bold'), 
                bg='#2d2d2d', fg='#ffffff').pack(anchor='w', pady=(0, 8))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(form_content, textvariable=self.password_var, 
                                      font=('Arial', 12), bg='#404040', fg='#ffffff',
                                      relief=tk.FLAT, bd=0, show='*', insertbackground='#ffffff')
        self.password_entry.pack(fill=tk.X, ipady=10, pady=(0, 15))
        
        # Campo Confirmar Contraseña (solo para registro)
        self.confirm_label = tk.Label(form_content, text="Confirmar Contraseña", 
                                     font=('Arial', 11, 'bold'), 
                                     bg='#2d2d2d', fg='#ffffff')
        
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = tk.Entry(form_content, textvariable=self.confirm_password_var, 
                                              font=('Arial', 12), bg='#404040', fg='#ffffff',
                                              relief=tk.FLAT, bd=0, show='*', insertbackground='#ffffff')
        
        # Botón principal
        self.main_btn = tk.Button(form_content, text="🔓 Entrar", 
                                 command=self.handle_main_action, font=('Arial', 12, 'bold'),
                                 bg='#007acc', fg='white', relief=tk.FLAT, 
                                 padx=25, pady=12, cursor='hand2',
                                 activebackground='#005999')
        self.main_btn.pack(fill=tk.X, pady=(8, 0))
        
        # Enlaces para cambiar modo
        links_frame = tk.Frame(form_content, bg='#2d2d2d')
        links_frame.pack(fill=tk.X, pady=(15, 0))  # Menos espacio arriba
        
        self.switch_label = tk.Label(links_frame, text="¿No tienes cuenta?", 
                                    font=('Arial', 10), bg='#2d2d2d', fg='#888888')
        self.switch_label.pack(side=tk.LEFT)
        
        self.switch_btn = tk.Button(links_frame, text="Crear cuenta", 
                                   command=self.toggle_mode, font=('Arial', 10, 'underline'),
                                   bg='#2d2d2d', fg='#007acc', relief=tk.FLAT, 
                                   bd=0, cursor='hand2', activebackground='#2d2d2d')
        self.switch_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # STATUS BAR - Mensajes de estado
        self.status_frame = tk.Frame(main_container, bg='#1e1e1e', height=30)
        self.status_frame.pack(fill=tk.X)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="", 
                                    font=('Arial', 10), bg='#1e1e1e')
        self.status_label.pack(expand=True)
        
        # Eventos de teclado
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus_set())
        self.password_entry.bind('<Return>', lambda e: self.handle_main_action())
        self.confirm_password_entry.bind('<Return>', lambda e: self.handle_main_action())
        
        # Focus inicial
        self.username_entry.focus_set()
        
        # Configurar modo inicial
        self.update_ui_mode()
    
    def toggle_mode(self):
        """Cambia entre modo login y registro"""
        if self.current_mode == "login":
            self.current_mode = "register"
        else:
            self.current_mode = "login"
        
        self.update_ui_mode()
        self.clear_status()
    
    def update_ui_mode(self):
        """Actualiza la interfaz según el modo actual"""
        if self.current_mode == "login":
            # Modo Login
            self.title_label.config(text="Iniciar Sesión")
            self.subtitle_label.config(text="Acceso seguro al sistema")
            self.main_btn.config(text="🔓 Entrar", bg='#007acc')
            self.switch_label.config(text="¿No tienes cuenta?")
            self.switch_btn.config(text="Crear cuenta")
            
            # Ocultar campo confirmar contraseña
            self.confirm_label.pack_forget()
            self.confirm_password_entry.pack_forget()
            
        else:
            # Modo Registro
            self.title_label.config(text="Crear Cuenta")
            self.subtitle_label.config(text="Registro de nuevo usuario")
            self.main_btn.config(text="✨ Registrarse", bg='#28a745')
            self.switch_label.config(text="¿Ya tienes cuenta?")
            self.switch_btn.config(text="Iniciar sesión")
            
            # Mostrar campo confirmar contraseña
            self.confirm_label.pack(anchor='w', pady=(0, 6))
            self.confirm_password_entry.pack(fill=tk.X, ipady=10, pady=(0, 15))
    
    def handle_main_action(self):
        """Maneja la acción principal (login o registro)"""
        if self.current_mode == "login":
            self.login()
        else:
            self.register()
    
    def show_status(self, message, status_type="info"):
        """Muestra mensaje de estado con colores"""
        colors = {
            "success": "#28a745",
            "error": "#dc3545", 
            "warning": "#ffc107",
            "info": "#17a2b8"
        }
        
        color = colors.get(status_type, "#888888")
        self.status_label.config(text=message, fg=color)
        
        # Auto-limpiar después de 5 segundos
        self.root.after(5000, self.clear_status)
    
    def clear_status(self):
        """Limpia el mensaje de estado"""
        self.status_label.config(text="")
    
    def hash_password(self, password):
        """Encripta la contraseña con bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def verify_password(self, hashed_password, password):
        """Verifica la contraseña"""
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    
    def is_user_blocked(self, username):
        """Verifica si el usuario está bloqueado"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT blocked_until FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result and result[0] > int(time.time()):
            return True
        return False
    
    def get_failed_attempts(self, username):
        """Obtiene el número de intentos fallidos"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT failed_attempts FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else 0
    
    def register(self):
        """Registra un nuevo usuario"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Validaciones
        if not username or not password:
            self.show_status("Por favor, completa todos los campos", "error")
            return
        
        if len(username) < 3:
            self.show_status("El usuario debe tener al menos 3 caracteres", "error")
            return
        
        if len(password) < 6:
            self.show_status("La contraseña debe tener al menos 6 caracteres", "error")
            return
        
        if password != confirm_password:
            self.show_status("Las contraseñas no coinciden", "error")
            return
        
        # Intentar registrar
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                          (username, self.hash_password(password)))
            conn.commit()
            conn.close()
            
            self.show_status(f"✅ Usuario '{username}' registrado exitosamente", "success")
            
            # Limpiar campos y cambiar a modo login
            self.username_var.set("")
            self.password_var.set("")
            self.confirm_password_var.set("")
            
            # Cambiar a modo login después de 2 segundos
            self.root.after(2000, lambda: (setattr(self, 'current_mode', 'login'), 
                                          self.update_ui_mode()))
            
        except sqlite3.IntegrityError:
            self.show_status("El usuario ya existe", "error")
        except Exception as e:
            self.show_status(f"Error al registrar: {str(e)}", "error")
    
    def login(self):
        """Realiza el login del usuario"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.show_status("Por favor, ingresa usuario y contraseña", "error")
            return
        
        # Verificar si está bloqueado
        if self.is_user_blocked(username):
            remaining_time = self.get_remaining_block_time(username)
            self.show_status(f"🔒 Usuario bloqueado. Intenta en {remaining_time}", "warning")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash, failed_attempts FROM users WHERE username = ?", 
                          (username,))
            user = cursor.fetchone()
            
            if user and self.verify_password(user[0], password):
                # Login exitoso
                cursor.execute("UPDATE users SET failed_attempts = 0, blocked_until = 0, last_login = ? WHERE username = ?", 
                              (datetime.now().isoformat(), username))
                
                # Registrar intento exitoso
                cursor.execute("INSERT INTO login_attempts (username, ip_address, success) VALUES (?, ?, ?)", 
                              (username, "localhost", 1))
                
                conn.commit()
                conn.close()
                
                self.show_status(f"🎉 ¡Bienvenido, {username}!", "success")
                
                # Mostrar ventana de éxito después de 1 segundo
                self.root.after(1000, lambda: self.show_success_window(username))
                
            else:
                # Login fallido
                if user:
                    failed_attempts = user[1] + 1
                    blocked_until = 0
                    
                    if failed_attempts >= self.MAX_ATTEMPTS:
                        blocked_until = int(time.time()) + self.BLOCK_TIME
                        self.show_status(f"🚫 Usuario bloqueado por {self.BLOCK_TIME//60} minutos", "error")
                    else:
                        remaining = self.MAX_ATTEMPTS - failed_attempts
                        self.show_status(f"❌ Contraseña incorrecta. Intentos restantes: {remaining}", "error")
                    
                    cursor.execute("UPDATE users SET failed_attempts = ?, blocked_until = ? WHERE username = ?", 
                                  (failed_attempts, blocked_until, username))
                else:
                    self.show_status("❌ Usuario no encontrado", "error")
                
                # Registrar intento fallido
                cursor.execute("INSERT INTO login_attempts (username, ip_address, success) VALUES (?, ?, ?)", 
                              (username, "localhost", 0))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            self.show_status(f"Error de conexión: {str(e)}", "error")
    
    def get_remaining_block_time(self, username):
        """Obtiene el tiempo restante de bloqueo"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT blocked_until FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result and result[0] > int(time.time()):
            remaining_seconds = result[0] - int(time.time())
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            return f"{minutes}m {seconds}s"
        
        return "0s"
    
    def show_success_window(self, username):
        """Muestra dashboard completo tras login exitoso"""
        # Cerrar ventana de login
        self.root.withdraw()
        
        # Crear dashboard a pantalla completa
        dashboard = tk.Toplevel()
        dashboard.title("🚀 Dashboard - Sistema Seguro")
        dashboard.configure(bg='#0a0a0a')
        dashboard.state('zoomed')  # Pantalla completa en Windows
        dashboard.attributes('-fullscreen', True)  # Pantalla completa en Linux/Mac
        
        # Variable para controlar el dashboard
        self.dashboard_window = dashboard
        
        # Obtener datos de usuarios
        users_data = self.get_all_users_data()
        user_stats = self.get_user_statistics()
        
        # HEADER PRINCIPAL - Barra superior
        header_frame = tk.Frame(dashboard, bg='#1a1a1a', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg='#1a1a1a')
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        # Logo y título izquierda
        left_header = tk.Frame(header_content, bg='#1a1a1a')
        left_header.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(left_header, text="🚀", font=('Arial', 32), 
                bg='#1a1a1a', fg='#00ff88').pack(side=tk.LEFT)
        
        welcome_frame = tk.Frame(left_header, bg='#1a1a1a')
        welcome_frame.pack(side=tk.LEFT, padx=(15, 0), fill=tk.Y)
        
        tk.Label(welcome_frame, text=f"¡Hola, {username}!", 
                font=('Arial', 20, 'bold'), bg='#1a1a1a', fg='#ffffff').pack(anchor='w')
        
        current_time = datetime.now().strftime("%H:%M - %d/%m/%Y")
        tk.Label(welcome_frame, text=f"📅 {current_time}", 
                font=('Arial', 12), bg='#1a1a1a', fg='#888888').pack(anchor='w')
        
        # Botones derecha del header
        right_header = tk.Frame(header_content, bg='#1a1a1a')
        right_header.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón salir a pantalla completa
        exit_btn = tk.Button(right_header, text="🚪 Salir", 
                            command=lambda: self.exit_dashboard(dashboard),
                            font=('Arial', 12, 'bold'), bg='#dc3545', fg='white',
                            relief=tk.FLAT, padx=20, pady=8, cursor='hand2',
                            activebackground='#c82333')
        exit_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botón minimizar pantalla completa
        minimize_btn = tk.Button(right_header, text="📱 Ventana", 
                                command=lambda: self.toggle_fullscreen(dashboard),
                                font=('Arial', 12, 'bold'), bg='#6c757d', fg='white',
                                relief=tk.FLAT, padx=20, pady=8, cursor='hand2',
                                activebackground='#545b62')
        minimize_btn.pack(side=tk.RIGHT)
        
        # MAIN CONTENT AREA
        main_content = tk.Frame(dashboard, bg='#0a0a0a')
        main_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # ESTADÍSTICAS - Tarjetas superiores
        stats_frame = tk.Frame(main_content, bg='#0a0a0a', height=120)
        stats_frame.pack(fill=tk.X, pady=(20, 30))
        stats_frame.pack_propagate(False)
        
        # Crear tarjetas de estadísticas con hover effect
        self.create_stat_card(stats_frame, "👥", "Total Usuarios", 
                             str(user_stats['total']), "#007acc", 0)
        self.create_stat_card(stats_frame, "✅", "Activos Hoy", 
                             str(user_stats['active_today']), "#28a745", 1)
        self.create_stat_card(stats_frame, "🚫", "Bloqueados", 
                             str(user_stats['blocked']), "#dc3545", 2)
        self.create_stat_card(stats_frame, "🔒", "Intentos Fallidos", 
                             str(user_stats['failed_attempts']), "#ffc107", 3)
        
        # TÍTULO SECCIÓN USUARIOS
        title_frame = tk.Frame(main_content, bg='#0a0a0a')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(title_frame, text="📋 Base de Datos de Usuarios", 
                font=('Arial', 18, 'bold'), bg='#0a0a0a', fg='#ffffff').pack(side=tk.LEFT)
        
        # Contador de usuarios
        count_label = tk.Label(title_frame, text=f"({len(users_data)} usuarios registrados)", 
                              font=('Arial', 12), bg='#0a0a0a', fg='#888888')
        count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # LISTA DE USUARIOS - Scrollable
        users_container = tk.Frame(main_content, bg='#0a0a0a')
        users_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar para hacer scroll
        canvas = tk.Canvas(users_container, bg='#0a0a0a', highlightthickness=0)
        scrollbar = ttk.Scrollbar(users_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0a0a0a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear tarjetas de usuarios con animaciones
        for i, user in enumerate(users_data):
            self.create_user_card(scrollable_frame, user, i)
        
        # Pack del canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind scroll del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Escape para salir de pantalla completa
        dashboard.bind('<Escape>', lambda e: self.exit_dashboard(dashboard))
        dashboard.focus_set()
    
    def create_stat_card(self, parent, icon, title, value, color, position):
        """Crea tarjeta de estadística con hover effect"""
        # Frame principal de la tarjeta
        card_frame = tk.Frame(parent, bg='#1a1a1a', relief=tk.FLAT)
        card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if position == 0 else 10, 0))
        
        # Contenido de la tarjeta
        content = tk.Frame(card_frame, bg='#1a1a1a')
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Icono
        icon_label = tk.Label(content, text=icon, font=('Arial', 28), 
                             bg='#1a1a1a', fg=color)
        icon_label.pack()
        
        # Valor principal
        value_label = tk.Label(content, text=value, font=('Arial', 24, 'bold'), 
                              bg='#1a1a1a', fg='#ffffff')
        value_label.pack()
        
        # Título
        title_label = tk.Label(content, text=title, font=('Arial', 10), 
                              bg='#1a1a1a', fg='#888888')
        title_label.pack()
        
        # Hover effects - simulados con bind
        def on_enter(e):
            card_frame.config(bg='#2a2a2a')
            content.config(bg='#2a2a2a')
            icon_label.config(bg='#2a2a2a')
            value_label.config(bg='#2a2a2a')
            title_label.config(bg='#2a2a2a')
        
        def on_leave(e):
            card_frame.config(bg='#1a1a1a')
            content.config(bg='#1a1a1a')
            icon_label.config(bg='#1a1a1a')
            value_label.config(bg='#1a1a1a')
            title_label.config(bg='#1a1a1a')
        
        # Bind hover events a todos los elementos
        for widget in [card_frame, content, icon_label, value_label, title_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def create_user_card(self, parent, user, index):
        """Crea tarjeta de usuario con animaciones hover"""
        # Frame principal de la tarjeta
        card_frame = tk.Frame(parent, bg='#1a1a1a', relief=tk.FLAT, height=100)
        card_frame.pack(fill=tk.X, pady=(0, 15), padx=20)
        card_frame.pack_propagate(False)
        
        # Contenido interno
        content = tk.Frame(card_frame, bg='#1a1a1a')
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # IZQUIERDA - Avatar y info principal
        left_section = tk.Frame(content, bg='#1a1a1a')
        left_section.pack(side=tk.LEFT, fill=tk.Y)
        
        # Avatar generado
        avatar_colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7", "#dda0dd"]
        avatar_color = avatar_colors[index % len(avatar_colors)]
        
        avatar_frame = tk.Frame(left_section, bg=avatar_color, width=60, height=60)
        avatar_frame.pack(side=tk.LEFT)
        avatar_frame.pack_propagate(False)
        
        # Inicial del usuario
        initial = user['username'][0].upper()
        tk.Label(avatar_frame, text=initial, font=('Arial', 24, 'bold'), 
                bg=avatar_color, fg='white').pack(expand=True)
        
        # Info del usuario
        info_frame = tk.Frame(left_section, bg='#1a1a1a')
        info_frame.pack(side=tk.LEFT, padx=(20, 0), fill=tk.Y)
        
        # Nombre de usuario
        username_label = tk.Label(info_frame, text=f"@{user['username']}", 
                                 font=('Arial', 16, 'bold'), bg='#1a1a1a', fg='#ffffff')
        username_label.pack(anchor='w')
        
        # Fecha de registro
        created_label = tk.Label(info_frame, text=f"📅 Desde: {user['created_at']}", 
                                font=('Arial', 10), bg='#1a1a1a', fg='#888888')
        created_label.pack(anchor='w')
        
        # Último login
        last_login = user['last_login'] if user['last_login'] else "Nunca"
        login_label = tk.Label(info_frame, text=f"🔑 Último acceso: {last_login}", 
                              font=('Arial', 10), bg='#1a1a1a', fg='#888888')
        login_label.pack(anchor='w')
        
        # DERECHA - Estado y estadísticas
        right_section = tk.Frame(content, bg='#1a1a1a')
        right_section.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Estado del usuario
        is_blocked = user['blocked_until'] > int(time.time())
        status_color = "#dc3545" if is_blocked else "#28a745"
        status_text = "🚫 BLOQUEADO" if is_blocked else "✅ ACTIVO"
        
        status_label = tk.Label(right_section, text=status_text, 
                               font=('Arial', 12, 'bold'), bg='#1a1a1a', fg=status_color)
        status_label.pack(anchor='e')
        
        # Intentos fallidos
        attempts_text = f"❌ Intentos fallidos: {user['failed_attempts']}"
        attempts_label = tk.Label(right_section, text=attempts_text, 
                                 font=('Arial', 10), bg='#1a1a1a', fg='#888888')
        attempts_label.pack(anchor='e')
        
        # ID del usuario
        id_label = tk.Label(right_section, text=f"ID: #{user['id']}", 
                           font=('Arial', 9), bg='#1a1a1a', fg='#666666')
        id_label.pack(anchor='e')
        
        # HOVER EFFECTS con animación
        def on_enter(e):
            # Cambiar color de fondo con efecto
            card_frame.config(bg='#2a2a2a')
            content.config(bg='#2a2a2a')
            left_section.config(bg='#2a2a2a')
            info_frame.config(bg='#2a2a2a')
            right_section.config(bg='#2a2a2a')
            
            # Cambiar color de labels
            for label in [username_label, created_label, login_label, 
                         status_label, attempts_label, id_label]:
                label.config(bg='#2a2a2a')
            
            # Efecto de "elevación" simulado
            card_frame.config(relief=tk.RAISED, bd=2)
        
        def on_leave(e):
            # Volver al color original
            card_frame.config(bg='#1a1a1a', relief=tk.FLAT, bd=0)
            content.config(bg='#1a1a1a')
            left_section.config(bg='#1a1a1a')
            info_frame.config(bg='#1a1a1a')
            right_section.config(bg='#1a1a1a')
            
            # Restaurar labels
            for label in [username_label, created_label, login_label, 
                         status_label, attempts_label, id_label]:
                label.config(bg='#1a1a1a')
        
        # Click effect (opcional)
        def on_click(e):
            # Pequeña animación de click
            card_frame.config(bg='#3a3a3a')
            parent.after(100, lambda: card_frame.config(bg='#2a2a2a'))
        
        # Bind eventos a todos los elementos de la tarjeta
        all_widgets = [card_frame, content, left_section, info_frame, right_section,
                      username_label, created_label, login_label, status_label, 
                      attempts_label, id_label]
        
        for widget in all_widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
    
    def get_all_users_data(self):
        """Obtiene todos los datos de usuarios de la base de datos"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("""SELECT id, username, created_at, last_login, 
                                failed_attempts, blocked_until 
                         FROM users ORDER BY created_at DESC""")
        users = cursor.fetchall()
        
        conn.close()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user[0],
                'username': user[1],
                'created_at': user[2][:10] if user[2] else "N/A",  # Solo fecha
                'last_login': user[3][:16] if user[3] else None,    # Fecha y hora
                'failed_attempts': user[4],
                'blocked_until': user[5]
            })
        
        return users_data
    
    def get_user_statistics(self):
        """Calcula estadísticas de usuarios"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Total usuarios
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        
        # Usuarios activos hoy (que han hecho login hoy)
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(last_login) = ?", (today,))
        active_today = cursor.fetchone()[0]
        
        # Usuarios bloqueados
        current_time = int(time.time())
        cursor.execute("SELECT COUNT(*) FROM users WHERE blocked_until > ?", (current_time,))
        blocked = cursor.fetchone()[0]
        
        # Total intentos fallidos (suma de todos)
        cursor.execute("SELECT SUM(failed_attempts) FROM users")
        failed_attempts = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total': total,
            'active_today': active_today,
            'blocked': blocked,
            'failed_attempts': failed_attempts
        }
    
    def toggle_fullscreen(self, window):
        """Alterna entre pantalla completa y ventana normal"""
        current_state = window.attributes('-fullscreen')
        window.attributes('-fullscreen', not current_state)
        
        if not current_state:  # Si no estaba en pantalla completa
            window.state('normal')
            window.geometry("1200x800")
    
    def exit_dashboard(self, dashboard):
        """Sale del dashboard y vuelve al login"""
        dashboard.destroy()
        self.root.deiconify()  # Mostrar ventana de login de nuevo
        
        # Limpiar campos
        self.username_var.set("")
        self.password_var.set("")
        self.username_entry.focus_set()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Cierre de la aplicación"""
        self.root.destroy()

if __name__ == "__main__":
    # Instalar bcrypt si no está disponible
    try:
        import bcrypt
    except ImportError:
        print("Instalando bcrypt...")
        os.system("pip install bcrypt")
        import bcrypt
    
    app = MinimalLoginSystem()
    app.run()