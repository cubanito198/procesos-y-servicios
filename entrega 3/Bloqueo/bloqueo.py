import sqlite3
import time
import bcrypt

# Configuración
DB_NAME = "users.db"
MAX_ATTEMPTS = 3
BLOCK_TIME = 300  # 5 minutos en segundos

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY,
                      username TEXT UNIQUE,
                      password TEXT,
                      failed_attempts INTEGER DEFAULT 0,
                      last_attempt INTEGER DEFAULT 0,
                      blocked_until INTEGER DEFAULT 0
                      )''')
    conn.commit()
    return conn, cursor

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(hashed_password, password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def register(username, password):
    conn, cursor = connect_db()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        print("Usuario registrado exitosamente.")
    except sqlite3.IntegrityError:
        print("El usuario ya existe.")
    finally:
        conn.close()

def login(username, password):
    conn, cursor = connect_db()
    cursor.execute("SELECT password, failed_attempts, last_attempt, blocked_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        print("Usuario no encontrado.")
        return
    
    hashed_password, failed_attempts, last_attempt, blocked_until = user
    current_time = int(time.time())
    
    if blocked_until > current_time:
        print("Cuenta bloqueada. Inténtalo más tarde.")
        return
    
    if verify_password(hashed_password, password):
        print("Inicio de sesión exitoso.")
        cursor.execute("UPDATE users SET failed_attempts = 0, blocked_until = 0 WHERE username = ?", (username,))
    else:
        failed_attempts += 1
        if failed_attempts >= MAX_ATTEMPTS:
            blocked_until = current_time + BLOCK_TIME
            print("Cuenta bloqueada por múltiples intentos fallidos.")
        else:
            print("Contraseña incorrecta.")
        cursor.execute("UPDATE users SET failed_attempts = ?, last_attempt = ?, blocked_until = ? WHERE username = ?", 
                       (failed_attempts, current_time, blocked_until, username))
    conn.commit()
    conn.close()

# Prueba del sistema
if __name__ == "__main__":
    while True:
        option = input("Selecciona una opción: [R]egistrar / [L]ogin / [Q]uit: ").strip().lower()
        if option == "r":
            user = input("Usuario: ")
            pwd = input("Contraseña: ")
            register(user, pwd)
        elif option == "l":
            user = input("Usuario: ")
            pwd = input("Contraseña: ")
            login(user, pwd)
        elif option == "q":
            break