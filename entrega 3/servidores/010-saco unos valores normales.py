import psutil       # Para acceder a las estadísticas de red del sistema
import time         # Para manejar tiempos de espera y medir intervalos
import argparse     # Para parsear argumentos desde la línea de comandos

def measure_baseline(interval, baseline_count):
    """
    Calcula los valores promedio de subida y bajada (baseline) durante un período de referencia.
    
    Parámetros:
        interval (float): Tiempo en segundos entre cada medición.
        baseline_count (int): Número de mediciones para calcular el promedio.
    
    Retorna:
        tuple: (avg_upload, avg_download, initial_net_io)
            avg_upload: Promedio de bytes enviados por segundo.
            avg_download: Promedio de bytes recibidos por segundo.
            initial_net_io: Estadísticas de red al finalizar la medición (para continuar el monitoreo).
    """
    print("Empezamos el cálculo de valores normales (baseline)...")
    initial_net_io = psutil.net_io_counters()
    time.sleep(interval)
    
    total_upload = 0
    total_download = 0

    for _ in range(baseline_count):
        net_io = psutil.net_io_counters()
        # Se suma la diferencia entre la medición actual e inicial (bytes enviados/recibidos en el intervalo)
        total_upload += (net_io.bytes_sent - initial_net_io.bytes_sent) / interval
        total_download += (net_io.bytes_recv - initial_net_io.bytes_recv) / interval
        
        # Actualizamos para la siguiente medición
        initial_net_io = net_io
        time.sleep(interval)
    
    avg_upload = total_upload / baseline_count
    avg_download = total_download / baseline_count
    return avg_upload, avg_download, initial_net_io

def monitor_network(interval, baseline_upload, baseline_download, initial_net_io, threshold, duration=15, log_file=None):
    """
    Monitorea la red y detecta anomalías si las velocidades instantáneas superan el baseline multiplicado por 'threshold'.
    
    Parámetros:
        interval (float): Tiempo en segundos entre cada medición.
        baseline_upload (float): Valor de referencia para la velocidad de subida (en bytes/seg).
        baseline_download (float): Valor de referencia para la velocidad de bajada (en bytes/seg).
        initial_net_io: Estadísticas de red de la última medición del baseline.
        threshold (float): Factor multiplicador para detectar anomalías.
        duration (float, opcional): Duración total del monitoreo en segundos. Si es None, se ejecuta indefinidamente.
        log_file (str, opcional): Ruta a un archivo donde se registrarán las anomalías detectadas.
    """
    # Si se especifica un archivo de log, se abre para escritura
    if log_file:
        try:
            log_f = open(log_file, mode='w')
            log_f.write("Timestamp,Upload (B/s),Download (B/s)\n")
        except Exception as e:
            print(f"Error al abrir el archivo de log: {e}")
            log_f = None
    else:
        log_f = None

    print("Ahora comenzamos la toma de datos en tiempo real...")
    start_time = time.time()
    current_net_io = initial_net_io

    try:
        while True:
            current_time = time.time()
            # Si se ha establecido una duración máxima, se finaliza cuando se alcanza
            if duration is not None and (current_time - start_time) >= duration:
                print("Duración de monitoreo alcanzada.")
                break

            net_io = psutil.net_io_counters()
            # Cálculo de las velocidades instantáneas (bytes/seg) en función de la diferencia
            current_upload = (net_io.bytes_sent - current_net_io.bytes_sent) / interval
            current_download = (net_io.bytes_recv - current_net_io.bytes_recv) / interval
            
            # Se comprueba si alguna velocidad supera el baseline multiplicado por el threshold
            if current_upload > baseline_upload * threshold or current_download > baseline_download * threshold:
                print(f"Anomalía detectada! Subida: {current_upload:.2f} B/s, Bajada: {current_download:.2f} B/s")
                if log_f:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    log_f.write(f"{timestamp},{current_upload:.2f},{current_download:.2f}\n")
                    log_f.flush()
            else:
                print(f"Normal: Subida: {current_upload:.2f} B/s, Bajada: {current_download:.2f} B/s")
            
            # Actualizamos el contador para la siguiente medición
            current_net_io = net_io
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
    finally:
        if log_f:
            log_f.close()

def main():
    # Configuración de los argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="Monitorea la red y detecta anomalías basadas en un baseline de uso normal."
    )
    parser.add_argument("--interval", type=float, default=1,
                        help="Intervalo entre mediciones en segundos (por defecto: 1)")
    parser.add_argument("--baseline_count", type=int, default=10,
                        help="Número de mediciones para calcular el baseline (por defecto: 10)")
    parser.add_argument("--threshold", type=float, default=5.0,
                        help="Multiplicador para detectar anomalías (por defecto: 5)")
    parser.add_argument("--duration", type=float, default=None,
                        help="Duración total del monitoreo en segundos (por defecto: indefinido)")
    parser.add_argument("--log", type=str, default=None,
                        help="Ruta al archivo para registrar anomalías (por ejemplo, anomalies.log)")
    
    args = parser.parse_args()

    # Cálculo de los valores de referencia (baseline)
    baseline_upload, baseline_download, initial_net_io = measure_baseline(args.interval, args.baseline_count)
    print(f"Valores promedio (baseline):")
    print(f"  Subida: {baseline_upload:.2f} B/s")
    print(f"  Bajada: {baseline_download:.2f} B/s")
    
    # Inicia el monitoreo en tiempo real
    monitor_network(args.interval, baseline_upload, baseline_download, initial_net_io,
                    args.threshold, args.duration, args.log)

if __name__ == "__main__":
    main()
