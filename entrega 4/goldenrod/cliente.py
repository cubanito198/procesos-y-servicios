import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import json
from datetime import datetime
import queue
import time

class MinimalTCPClient:
    def __init__(self):
        self.config = self.load_config()
        self.connected = False
        self.socket = None
        self.username = ""
        self.message_queue = queue.Queue()
        
        # Variables para función "escribiendo..."
        self.typing_timer = None
        self.typing_users = set()
        self.last_typing_time = 0
        self.typing_sent = False
        
        # Crear la interfaz gráfica minimalista
        self.setup_gui()
        
        # Iniciar el procesador de mensajes
        self.start_message_processor()
        
    def load_config(self):
        """Carga configuración del cliente"""
        default_config = {
            "server_host": "localhost",
            "server_port": 3000  # ✅ PUERTO 3000 POR DEFECTO
        }
        
        try:
            with open('client_config.json', 'r') as f:
                config = json.load(f)
            return {**default_config, **config}
        except:
            return default_config
    
    def save_config(self):
        """✅ NUEVO: Guarda la configuración actual"""
        config = {
            "server_host": self.host_var.get(),
            "server_port": int(self.port_var.get()) if self.port_var.get().isdigit() else 3000
        }
        
        try:
            with open('client_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def setup_gui(self):
        """Diseño minimalista y moderno"""
        self.root = tk.Tk()
        self.root.title("Chat")
        self.root.geometry("500x700")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(True, True)
        
        # Crear el container principal
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # HEADER - Barra superior ultra minimalista
        header = tk.Frame(main_container, bg='#2d2d2d', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Contenido del header en una sola línea
        header_content = tk.Frame(header, bg='#2d2d2d')
        header_content.pack(expand=True, fill='both', padx=15, pady=10)
        
        # Status y título
        self.status_dot = tk.Label(header_content, text="●", font=('Arial', 16), 
                                   fg='#ff4444', bg='#2d2d2d')
        self.status_dot.pack(side=tk.LEFT)
        
        title = tk.Label(header_content, text="Chat Room", font=('Arial', 14, 'bold'), 
                        fg='#ffffff', bg='#2d2d2d')
        title.pack(side=tk.LEFT, padx=(8, 0))
        
        # Conexión rápida (lado derecho)
        connection_frame = tk.Frame(header_content, bg='#2d2d2d')
        connection_frame.pack(side=tk.RIGHT)
        
        # Campo usuario (más pequeño)
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(connection_frame, textvariable=self.username_var, 
                                 font=('Arial', 9), bg='#404040', fg='#ffffff', 
                                 relief=tk.FLAT, width=12, insertbackground='#ffffff')
        username_entry.pack(side=tk.LEFT, padx=(0, 8))
        username_entry.insert(0, "tu nombre")
        username_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(username_entry, "tu nombre"))
        
        # Botón conectar minimalista
        self.connect_btn = tk.Button(connection_frame, text="Conectar", 
                                    command=self.connect_to_server, font=('Arial', 9),
                                    bg='#007acc', fg='white', relief=tk.FLAT, 
                                    padx=15, pady=5, cursor='hand2',
                                    activebackground='#005999')
        self.connect_btn.pack(side=tk.LEFT)
        
        # Botón desconectar (inicialmente oculto)
        self.disconnect_btn = tk.Button(connection_frame, text="Desconectar", 
                                       command=self.disconnect_from_server, font=('Arial', 9),
                                       bg='#dc3545', fg='white', relief=tk.FLAT, 
                                       padx=12, pady=5, cursor='hand2',
                                       activebackground='#c82333')
        # No empaquetarlo inicialmente
        
        # CHAT AREA - El foco principal
        chat_container = tk.Frame(main_container, bg='#1e1e1e')
        chat_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Área de mensajes (versión más compatible)
        self.chat_text = scrolledtext.ScrolledText(chat_container, 
                                                  font=('Arial', 11),
                                                  bg='#1e1e1e', fg='#e0e0e0', 
                                                  relief=tk.FLAT, bd=0, wrap=tk.WORD,
                                                  state=tk.DISABLED,
                                                  insertbackground='#ffffff')
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 5))
        
        # ✅ NUEVO: Área para mostrar "escribiendo..." como WhatsApp
        self.typing_frame = tk.Frame(chat_container, bg='#1e1e1e', height=25)
        self.typing_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
        self.typing_frame.pack_propagate(False)
        
        self.typing_label = tk.Label(self.typing_frame, text="", font=('Arial', 9, 'italic'), 
                                    fg='#888888', bg='#1e1e1e', anchor='w')
        self.typing_label.pack(fill=tk.X)
        
        # INPUT AREA - Barra inferior elegante
        input_container = tk.Frame(main_container, bg='#1e1e1e', height=80)
        input_container.pack(fill=tk.X, padx=20, pady=(0, 20))
        input_container.pack_propagate(False)
        
        # Frame para el input con borde redondeado simulado
        input_frame = tk.Frame(input_container, bg='#2d2d2d', relief=tk.FLAT)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Campo de mensaje elegante
        message_container = tk.Frame(input_frame, bg='#2d2d2d')
        message_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(message_container, textvariable=self.message_var, 
                                     font=('Arial', 12), bg='#2d2d2d', fg='#ffffff',
                                     relief=tk.FLAT, bd=0, state=tk.DISABLED,
                                     insertbackground='#ffffff')
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.message_entry.bind('<Return>', self.send_message_event)
        
        # ✅ NUEVO: Eventos para detectar cuando alguien está escribiendo
        self.message_entry.bind('<KeyPress>', self.on_key_press)
        self.message_entry.bind('<KeyRelease>', self.on_key_release)
        
        # Placeholder para el campo de mensaje
        self.message_entry.insert(0, "Conecta para chatear...")
        self.message_entry.config(fg='#666666')
        
        # Botón enviar minimalista
        self.send_btn = tk.Button(message_container, text="→", 
                                 command=self.send_message, font=('Arial', 14, 'bold'),
                                 bg='#007acc', fg='white', relief=tk.FLAT,
                                 width=3, height=1, cursor='hand2', state=tk.DISABLED,
                                 activebackground='#005999')
        self.send_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Variables ocultas para configuración
        self.host_var = tk.StringVar(value=self.config['server_host'])
        self.port_var = tk.StringVar(value=str(self.config['server_port']))
        
        # ✅ NUEVO: Vincular cambios para auto-guardado
        self.host_var.trace('w', self.on_config_change)
        self.port_var.trace('w', self.on_config_change)
        
        # Configuración avanzada (oculta, se abre con doble click en título)
        title.bind('<Double-1>', self.toggle_advanced_config)
        self.advanced_visible = False
        
        # Variables para estadísticas (ocultas en esta versión minimal)
        self.messages_sent = 0
        self.connect_time = None
        
        # Configurar colores del chat más suaves
        self.chat_text.tag_configure("sent", foreground="#87ceeb", font=('Segoe UI', 11))
        self.chat_text.tag_configure("received", foreground="#98fb98", font=('Segoe UI', 11))
        self.chat_text.tag_configure("system", foreground="#dda0dd", font=('Segoe UI', 10, 'italic'))
        self.chat_text.tag_configure("error", foreground="#ff6b6b", font=('Segoe UI', 11))
        self.chat_text.tag_configure("timestamp", foreground="#666666", font=('Segoe UI', 9))
        self.chat_text.tag_configure("join", foreground="#4ecdc4", font=('Segoe UI', 10, 'italic'))
        self.chat_text.tag_configure("leave", foreground="#ff8a80", font=('Segoe UI', 10, 'italic'))
        
    def on_config_change(self, *args):
        """✅ NUEVO: Auto-guarda cuando cambia la configuración"""
        # Pequeño delay para evitar guardar en cada tecla
        if hasattr(self, '_save_timer'):
            self.root.after_cancel(self._save_timer)
        self._save_timer = self.root.after(1000, self.save_config)
    
    def clear_placeholder(self, entry, placeholder):
        """Limpia el placeholder cuando se hace focus"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='#ffffff')
    
    # ✅ NUEVO: Funciones para detectar "escribiendo..." como WhatsApp
    def on_key_press(self, event):
        """Detecta cuando el usuario está escribiendo"""
        if not self.connected:
            return
        
        # Si es Enter, no enviar typing
        if event.keysym == 'Return':
            return
        
        current_time = time.time()
        self.last_typing_time = current_time
        
        # Solo enviar una vez cada 3 segundos
        if not self.typing_sent:
            self.send_typing_signal()
            self.typing_sent = True
            
        # Programar stop typing después de 3 segundos de inactividad
        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)
        self.typing_timer = self.root.after(3000, self.stop_typing_signal)
    
    def on_key_release(self, event):
        """Detecta cuando el usuario para de escribir"""
        if not self.connected:
            return
        
        # Si el campo está vacío, parar de escribir inmediatamente
        if not self.message_var.get().strip():
            self.stop_typing_signal()
    
    def send_typing_signal(self):
        """Envía señal de que está escribiendo"""
        if self.connected and self.socket:
            try:
                typing_msg = f"TYPING:{self.username}"
                self.socket.send(typing_msg.encode('utf-8'))
            except:
                pass
    
    def stop_typing_signal(self):
        """Para la señal de escribiendo"""
        if self.connected and self.socket:
            try:
                stop_typing_msg = f"STOP_TYPING:{self.username}"
                self.socket.send(stop_typing_msg.encode('utf-8'))
            except:
                pass
        self.typing_sent = False
        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)
            self.typing_timer = None
    
    def update_typing_display(self):
        """Actualiza el display de "escribiendo..." """
        if self.typing_users:
            if len(self.typing_users) == 1:
                user = list(self.typing_users)[0]
                self.typing_label.config(text=f"📝 {user} está escribiendo...")
            else:
                users_list = ", ".join(list(self.typing_users)[:2])
                if len(self.typing_users) > 2:
                    self.typing_label.config(text=f"📝 {users_list} y {len(self.typing_users)-2} más están escribiendo...")
                else:
                    self.typing_label.config(text=f"📝 {users_list} están escribiendo...")
        else:
            self.typing_label.config(text="")
    
    def toggle_advanced_config(self, event=None):
        """Muestra/oculta configuración avanzada"""
        if not self.advanced_visible:
            # ✅ MEJORADO: Ventana MUY grande para que quepan todos los botones
            config_window = tk.Toplevel(self.root)
            config_window.title("Configuración")
            config_window.geometry("520x750")  # ✅ MÁS GRANDE TODAVÍA
            config_window.configure(bg='#2d2d2d')
            config_window.resizable(True, True)  # ✅ Permitir redimensionar por si acaso
            
            # Centrar ventana
            config_window.transient(self.root)
            config_window.grab_set()
            
            # ✅ NUEVO: Centrar la ventana en la pantalla
            config_window.update_idletasks()
            width = config_window.winfo_width()
            height = config_window.winfo_height()
            x = (config_window.winfo_screenwidth() // 2) - (width // 2)
            y = (config_window.winfo_screenheight() // 2) - (height // 2)
            config_window.geometry(f'{520}x{750}+{x}+{y}')
            
            # Título principal
            main_title = tk.Label(config_window, text="⚙️ Configuración de Conexión", 
                                 font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d')
            main_title.pack(pady=(25, 20))
            
            # Configuración básica
            basic_frame = tk.Frame(config_window, bg='#2d2d2d')
            basic_frame.pack(pady=(0, 25), padx=40, fill=tk.X)
            
            tk.Label(basic_frame, text="Servidor:", font=('Arial', 12, 'bold'),
                    fg='#ffffff', bg='#2d2d2d').pack(anchor='w', pady=(0, 8))
            host_entry = tk.Entry(basic_frame, textvariable=self.host_var, font=('Arial', 11),
                                 bg='#404040', fg='#ffffff', relief=tk.FLAT, bd=5)
            host_entry.pack(pady=(0, 15), fill=tk.X, ipady=8)
            
            tk.Label(basic_frame, text="Puerto:", font=('Arial', 12, 'bold'),
                    fg='#ffffff', bg='#2d2d2d').pack(anchor='w', pady=(0, 8))
            port_entry = tk.Entry(basic_frame, textvariable=self.port_var, font=('Arial', 11),
                                 bg='#404040', fg='#ffffff', relief=tk.FLAT, bd=5)
            port_entry.pack(pady=(0, 15), fill=tk.X, ipady=8)
            
            # ✅ ACTUALIZADO: Información Radmin VPN (sin LocalTunnel)
            separator = tk.Frame(config_window, bg='#404040', height=2)
            separator.pack(fill=tk.X, padx=40, pady=(0, 20))
            
            info_title = tk.Label(config_window, text="🌐 Tipos de Conexión", 
                                 font=('Arial', 14, 'bold'), fg='#28a745', bg='#2d2d2d')
            info_title.pack(pady=(0, 15))
            
            info_frame = tk.Frame(config_window, bg='#2d2d2d')
            info_frame.pack(pady=(0, 25), padx=40, fill=tk.X)
            
            info_text = tk.Text(info_frame, font=('Arial', 9), bg='#1e1e1e', fg='#e0e0e0',
                               relief=tk.FLAT, bd=0, wrap=tk.WORD, height=8, state=tk.DISABLED)  # ✅ Reducido de 10 a 8
            info_text.pack(fill=tk.X)
            
            # ✅ REDUCIDO: Información más compacta para dar espacio a botones
            info_content = """🏠 LOCAL: localhost • Puerto: 3000

🌐 RADMIN VPN: 
   • Instalar Radmin VPN (gratis)
   • IP de Radmin: 25.x.x.x • Puerto: 3000

🖥️ DIRECCIÓN IP:
   • Red local: 192.168.1.x
   • Internet: cualquier IP • Puerto: 3000"""
            
            info_text.config(state=tk.NORMAL)
            info_text.insert(tk.END, info_content)
            info_text.config(state=tk.DISABLED)
            
            # ✅ NUEVO: Separador antes de los botones para mayor claridad
            separator2 = tk.Frame(config_window, bg='#404040', height=2)
            separator2.pack(fill=tk.X, padx=40, pady=(20, 10))
            
            # Título para los botones
            buttons_title = tk.Label(config_window, text="⚡ Configuración Rápida", 
                                   font=('Arial', 12, 'bold'), fg='#ffffff', bg='#2d2d2d')
            buttons_title.pack(pady=(0, 15))
            
            # ✅ MEJORADO: Botones de configuración rápida con más espacio
            button_frame = tk.Frame(config_window, bg='#2d2d2d')
            button_frame.pack(pady=(25, 35))  # ✅ Más espacio arriba y abajo
            
            # Configuraciones rápidas
            quick_frame = tk.Frame(button_frame, bg='#2d2d2d')
            quick_frame.pack(pady=(0, 25))  # ✅ Más espacio entre botones y botón guardar
            
            def set_local():
                self.host_var.set("localhost")
                self.port_var.set("3000")
                self.save_config()  # ✅ AUTO-GUARDAR
            
            def set_radmin():
                # Ventana para pedir IP de Radmin VPN
                radmin_window = tk.Toplevel(config_window)
                radmin_window.title("Radmin VPN")
                radmin_window.geometry("400x280")
                radmin_window.configure(bg='#2d2d2d')
                radmin_window.resizable(False, False)
                radmin_window.transient(config_window)
                radmin_window.grab_set()
                
                tk.Label(radmin_window, text="🌐 Configurar Radmin VPN", 
                        font=('Arial', 14, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(pady=(25, 15))
                
                tk.Label(radmin_window, text="Introduce la IP de Radmin de tu amigo:", 
                        font=('Arial', 10), fg='#bdc3c7', bg='#2d2d2d').pack(pady=(0, 15))
                
                ip_var = tk.StringVar()
                ip_entry = tk.Entry(radmin_window, textvariable=ip_var, font=('Arial', 12), 
                                   bg='#404040', fg='#ffffff', width=30, relief=tk.FLAT, bd=5)
                ip_entry.pack(pady=(0, 10), ipady=8)
                ip_entry.insert(0, "25.123.45.67")
                ip_entry.focus_set()
                
                tk.Label(radmin_window, text="(Aparece en su Radmin VPN)", 
                        font=('Arial', 9), fg='#888888', bg='#2d2d2d').pack(pady=(0, 20))
                
                def apply_radmin():
                    ip = ip_var.get().strip()
                    if ip:
                        self.host_var.set(ip)
                        self.port_var.set("3000")
                        self.save_config()  # ✅ AUTO-GUARDAR
                        radmin_window.destroy()
                
                tk.Button(radmin_window, text="✅ Aplicar", command=apply_radmin,
                         font=('Arial', 12, 'bold'), bg='#28a745', fg='white', 
                         relief=tk.FLAT, padx=30, pady=12).pack(pady=20)
            
            # ✅ NUEVO: Botón para dirección IP personalizada
            def set_custom_ip():
                # ✅ ARREGLADO: Ventana más grande para ver el botón
                ip_window = tk.Toplevel(config_window)
                ip_window.title("Dirección IP Personalizada")
                ip_window.geometry("450x400")  # ✅ MÁS GRANDE
                ip_window.configure(bg='#2d2d2d')
                ip_window.resizable(True, True)  # ✅ Redimensionable por si acaso
                ip_window.transient(config_window)
                ip_window.grab_set()
                
                # ✅ CENTRAR la ventana
                ip_window.update_idletasks()
                x = (ip_window.winfo_screenwidth() // 2) - (225)  # 450/2 = 225
                y = (ip_window.winfo_screenheight() // 2) - (200)  # 400/2 = 200
                ip_window.geometry(f'450x400+{x}+{y}')
                
                tk.Label(ip_window, text="🖥️ Dirección IP Personalizada", 
                        font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(pady=(30, 20))
                
                tk.Label(ip_window, text="Introduce la dirección IP del servidor:", 
                        font=('Arial', 11), fg='#bdc3c7', bg='#2d2d2d').pack(pady=(0, 15))
                
                # ✅ MEJORADO: Campo IP más grande
                ip_frame = tk.Frame(ip_window, bg='#2d2d2d')
                ip_frame.pack(pady=(0, 20), padx=40, fill=tk.X)
                
                tk.Label(ip_frame, text="IP del Servidor:", font=('Arial', 10, 'bold'),
                        fg='#ffffff', bg='#2d2d2d').pack(anchor='w', pady=(0, 5))
                
                ip_var = tk.StringVar()
                ip_entry = tk.Entry(ip_frame, textvariable=ip_var, font=('Arial', 12), 
                                   bg='#404040', fg='#ffffff', relief=tk.FLAT, bd=5)
                ip_entry.pack(fill=tk.X, ipady=10, pady=(0, 20))
                ip_entry.insert(0, "192.168.1.100")
                ip_entry.focus_set()
                ip_entry.select_range(0, tk.END)  # ✅ Seleccionar todo el texto
                
                tk.Label(ip_frame, text="Puerto:", font=('Arial', 10, 'bold'),
                        fg='#ffffff', bg='#2d2d2d').pack(anchor='w', pady=(0, 5))
                
                port_var = tk.StringVar()
                port_entry = tk.Entry(ip_frame, textvariable=port_var, font=('Arial', 12), 
                                     bg='#404040', fg='#ffffff', relief=tk.FLAT, bd=5)
                port_entry.pack(fill=tk.X, ipady=10, pady=(0, 20))
                port_entry.insert(0, "3000")
                
                tk.Label(ip_window, text="Ejemplos: 192.168.1.100, 203.45.67.89, 25.123.45.67", 
                        font=('Arial', 9), fg='#888888', bg='#2d2d2d').pack(pady=(0, 30))
                
                # ✅ SUPER ARREGLADO: Botón GIGANTE que es imposible no ver
                def apply_custom():
                    ip = ip_var.get().strip()
                    port = port_var.get().strip()
                    if ip and port:
                        self.host_var.set(ip)
                        self.port_var.set(port)
                        self.save_config()  # ✅ GUARDAR INMEDIATAMENTE
                        
                        # ✅ CONFIRMACIÓN VISUAL
                        tk.messagebox.showinfo("✅ Configuración Guardada", 
                                             f"Servidor: {ip}:{port}\n\n¡Configuración guardada correctamente!")
                        ip_window.destroy()
                    else:
                        tk.messagebox.showerror("❌ Error", "Por favor introduce IP y Puerto válidos")
                
                # ✅ FRAME para botones con mejor espaciado
                button_frame = tk.Frame(ip_window, bg='#2d2d2d')
                button_frame.pack(pady=20)
                
                # ✅ BOTÓN SÚPER GRANDE Y VISIBLE
                apply_btn = tk.Button(button_frame, text="✅ APLICAR CONFIGURACIÓN", 
                                     command=apply_custom,
                                     font=('Arial', 14, 'bold'), bg='#28a745', fg='white', 
                                     relief=tk.FLAT, padx=40, pady=15, cursor='hand2',
                                     width=25, activebackground='#1e7e34')
                apply_btn.pack(pady=10)
                
                # ✅ Botón para cancelar
                cancel_btn = tk.Button(button_frame, text="❌ Cancelar", 
                                      command=ip_window.destroy,
                                      font=('Arial', 10), bg='#6c757d', fg='white', 
                                      relief=tk.FLAT, padx=20, pady=8, cursor='hand2')
                cancel_btn.pack(pady=(5, 0))
                
                # ✅ ATAJO: Enter para aplicar
                def on_enter(event):
                    apply_custom()
                
                ip_entry.bind('<Return>', on_enter)
                port_entry.bind('<Return>', on_enter)
            
            # ✅ MEJORADO: Botones más grandes y mejor organizados
            buttons_row1 = tk.Frame(quick_frame, bg='#2d2d2d')
            buttons_row1.pack(pady=(0, 12))
            
            tk.Button(buttons_row1, text="🏠 Local", command=set_local,
                     font=('Arial', 11, 'bold'), bg='#17a2b8', fg='white', 
                     relief=tk.FLAT, padx=25, pady=12, cursor='hand2',
                     width=12).pack(side=tk.LEFT, padx=(0, 15))
            
            tk.Button(buttons_row1, text="🌐 Radmin VPN", command=set_radmin,
                     font=('Arial', 11, 'bold'), bg='#28a745', fg='white', 
                     relief=tk.FLAT, padx=25, pady=12, cursor='hand2',
                     width=12).pack(side=tk.LEFT, padx=(0, 15))
            
            # ✅ NUEVO: Tercer botón para IP personalizada
            tk.Button(buttons_row1, text="🖥️ Dirección IP", command=set_custom_ip,
                     font=('Arial', 11, 'bold'), bg='#6f42c1', fg='white', 
                     relief=tk.FLAT, padx=25, pady=12, cursor='hand2',
                     width=12).pack(side=tk.LEFT)
            
            # ✅ SÚPER MEJORADO: Botón Guardar GIGANTE y súper visible
            def save_and_close():
                self.save_config()
                config_window.destroy()
            
            # Separador antes del botón guardar
            separator3 = tk.Frame(config_window, bg='#404040', height=1)
            separator3.pack(fill=tk.X, padx=40, pady=(15, 20))
            
            tk.Button(button_frame, text="💾 GUARDAR CONFIGURACIÓN", command=save_and_close,
                     font=('Arial', 16, 'bold'), bg='#007acc', fg='white', 
                     relief=tk.FLAT, padx=50, pady=20, cursor='hand2',
                     width=20, activebackground='#005999').pack(pady=15)
            
            # Añadir texto informativo bajo el botón
            tk.Label(button_frame, text="La configuración se guarda automáticamente", 
                    font=('Arial', 9), fg='#888888', bg='#2d2d2d').pack(pady=(5, 10))
    
    def start_message_processor(self):
        """Procesador de mensajes para la GUI"""
        def process_messages():
            try:
                while True:
                    message_type, data = self.message_queue.get(timeout=0.1)
                    if message_type == "chat":
                        self.add_chat_message(data[0], data[1])
                    elif message_type == "typing":
                        self.handle_typing_message(data)
                    self.message_queue.task_done()
            except queue.Empty:
                pass
            
            self.root.after(100, process_messages)
        
        self.root.after(100, process_messages)
    
    def handle_typing_message(self, data):
        """Maneja mensajes de typing"""
        action, username = data
        
        if action == "start":
            self.typing_users.add(username)
        elif action == "stop":
            self.typing_users.discard(username)
        
        self.update_typing_display()
    
    def add_chat_message(self, message, tag="received"):
        """Añade mensaje al chat con estilo minimalista"""
        self.chat_text.config(state=tk.NORMAL)
        
        # Para mensajes de sistema (conexiones/desconexiones)
        if tag == "system":
            if "se ha unido" in message:
                tag = "join"
            elif "ha salido" in message:
                tag = "leave"
        
        # Formato más limpio - sin timestamps prominentes
        if tag in ["sent", "received"]:
            # Solo mostrar el mensaje, más limpio
            self.chat_text.insert(tk.END, f"{message}\n", tag)
        else:
            # Mensajes de sistema con icono
            self.chat_text.insert(tk.END, f"{message}\n", tag)
        
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
    def connect_to_server(self):
        """Conecta al servidor"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get())
            username = self.username_var.get().strip()
            
            if not username or username == "tu nombre":
                messagebox.showerror("Error", "Ingresa tu nombre")
                return
            
            # Crear socket y conectar
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((host, port))
            
            # Manejar solicitud de nombre de usuario
            welcome_msg = self.socket.recv(1024).decode('utf-8')
            if welcome_msg == "NOMBRE_USUARIO":
                self.socket.send(username.encode('utf-8'))
            
            self.connected = True
            self.username = username
            self.connect_time = datetime.now()
            
            # Limpiar typing users al conectar
            self.typing_users.clear()
            self.update_typing_display()
            
            # Actualizar interfaz - modo conectado
            self.connect_btn.pack_forget()  # Ocultar botón conectar
            self.disconnect_btn.pack(side=tk.LEFT)  # Mostrar botón desconectar
            self.status_dot.config(fg='#28a745')
            
            # Habilitar campo de mensaje
            self.message_entry.config(state=tk.NORMAL, fg='#ffffff')
            self.message_entry.delete(0, tk.END)
            self.message_entry.focus_set()
            self.send_btn.config(state=tk.NORMAL)
            
            # Mensaje de bienvenida más sutil
            self.message_queue.put(("chat", (f"Conectado como {username}", "system")))
            
            # Iniciar hilo para recibir mensajes
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar:\n{str(e)}")
    
    def disconnect_from_server(self):
        """Desconecta del servidor"""
        # Enviar stop typing antes de desconectar
        self.stop_typing_signal()
        
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Limpiar typing users
        self.typing_users.clear()
        self.update_typing_display()
        
        # Restaurar interfaz
        self.disconnect_btn.pack_forget()  # Ocultar botón desconectar
        self.connect_btn.pack(side=tk.LEFT)  # Mostrar botón conectar
        self.status_dot.config(fg='#ff4444')
        self.message_entry.config(state=tk.DISABLED, fg='#666666')
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, "Conecta para chatear...")
        self.send_btn.config(state=tk.DISABLED)
        
        self.message_queue.put(("chat", ("Desconectado", "system")))
    
    def send_message_event(self, event):
        """Envía mensaje con Enter"""
        self.send_message()
        return 'break'
    
    def send_message(self):
        """Envía mensaje al servidor"""
        if not self.connected:
            return
        
        message = self.message_var.get().strip()
        if not message:
            return
        
        try:
            # Parar typing signal antes de enviar mensaje
            self.stop_typing_signal()
            
            self.socket.send(message.encode('utf-8'))
            
            # Mostrar mensaje enviado de forma más sutil
            self.message_queue.put(("chat", (f"Tú: {message}", "sent")))
            
            # Limpiar campo
            self.message_var.set("")
            self.messages_sent += 1
            
        except Exception as e:
            self.message_queue.put(("chat", (f"Error enviando: {str(e)}", "error")))
            # No desconectar automáticamente, dejar que el usuario decida
    
    def receive_messages(self):
        """Recibe mensajes del servidor"""
        while self.connected:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                
                # ✅ NUEVO: Manejar mensajes de typing
                if message.startswith("TYPING:"):
                    username = message[7:]
                    if username != self.username:  # No mostrar nuestro propio typing
                        self.message_queue.put(("typing", ("start", username)))
                elif message.startswith("STOP_TYPING:"):
                    username = message[12:]
                    if username != self.username:
                        self.message_queue.put(("typing", ("stop", username)))
                elif message.startswith("BROADCAST:"):
                    # Mensaje de otro usuario
                    broadcast_msg = message[10:]
                    self.message_queue.put(("chat", (broadcast_msg, "received")))
                elif message.startswith("KICKED:"):
                    # Has sido expulsado
                    kick_reason = message[7:]
                    self.message_queue.put(("chat", (f"🔨 {kick_reason}", "error")))
                    # Desconectar automáticamente cuando te expulsan
                    self.root.after(2000, self.disconnect_from_server)  # Desconectar después de 2 segundos
                    break
                elif message == "MSG_OK":
                    # Confirmación silenciosa - no mostrar nada
                    pass
                else:
                    # Mensajes del sistema
                    self.message_queue.put(("chat", (message, "system")))
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.connected:
                    self.message_queue.put(("chat", (f"Error de conexión: {str(e)}", "error")))
                break
        
        # Limpiar typing users al perder conexión
        self.typing_users.clear()
        self.update_typing_display()
        
        # Mostrar que se perdió la conexión con opción de reconectar
        if self.connected:
            self.message_queue.put(("chat", ("⚠️ Conexión perdida. Haz clic en Desconectar para intentar de nuevo.", "error")))
            # Cambiar el estado visual pero mantener la conexión lógica
            self.status_dot.config(fg='#ff8800')  # Color naranja para indicar problema
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Añadir mensaje de bienvenida
        self.add_chat_message("👋 Bienvenido al chat. Conecta para empezar.", "system")
        current_host = self.config['server_host']
        current_port = self.config['server_port']
        self.add_chat_message(f"💡 Configuración actual: {current_host}:{current_port}", "system")
        
        self.root.mainloop()
    
    def on_closing(self):
        """Cierre de la aplicación"""
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()

if __name__ == "__main__":
    client = MinimalTCPClient()
    client.run()