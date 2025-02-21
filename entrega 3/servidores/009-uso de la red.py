import psutil       # Para acceder a estadísticas de red y otros datos del sistema
import time         # Para medir intervalos y manejar tiempos de espera
import argparse     # Para parsear argumentos de línea de comandos
import csv          # Para escribir los datos en un archivo CSV

def get_network_usage(interval=1, duration=15, log_file="prueba.csv"):
    """
    Monitorea y muestra el uso de ancho de banda de la red (velocidades de subida y bajada)
    en intervalos definidos. Opcionalmente, registra los datos en un archivo CSV y permite
    limitar el tiempo total de monitoreo.

    Parámetros:
        interval (float): Intervalo de tiempo en segundos entre mediciones (por defecto es 1 segundo).
        duration (float, opcional): Duración total en segundos para ejecutar el monitoreo.
                                    Si es None, se ejecuta indefinidamente hasta que el usuario interrumpa.
        log_file (str, opcional): Ruta al archivo CSV donde se guardarán los resultados.
    """
    # Mensaje inicial para el usuario
    print("Monitoreando el uso de ancho de banda de la red... (Presiona Ctrl+C para detener)")

    # Se obtiene el estado inicial de la red
    initial_net_io = psutil.net_io_counters()

    # Variables para acumular el total de bytes transferidos (se convertirán a KB)
    cumulative_upload = 0
    cumulative_download = 0

    # Configuración del archivo CSV si se especifica log_file
    if log_file:
        try:
            csv_file = open(log_file, mode='w', newline='')
            csv_writer = csv.writer(csv_file)
            # Escribir cabecera en el CSV
            csv_writer.writerow(["Timestamp", "Upload (KB/s)", "Download (KB/s)", "Cumulative Upload (KB)", "Cumulative Download (KB)"])
        except Exception as e:
            print(f"Error al abrir el archivo de log: {e}")
            csv_file = None
            csv_writer = None
    else:
        csv_file = None
        csv_writer = None

    # Se toma el tiempo inicial para calcular la duración total si se establece un límite
    start_time = time.time()
    # Se espera el intervalo inicial para tener una primera diferencia
    time.sleep(interval)

    try:
        while True:
            current_time = time.time()

            # Si se estableció una duración y se ha alcanzado el límite, se rompe el ciclo
            if duration is not None and (current_time - start_time) >= duration:
                print("Duración de monitoreo alcanzada.")
                break

            # Se obtienen las estadísticas actuales de I/O de red
            net_io = psutil.net_io_counters()

            # Se calcula la diferencia en bytes enviados y recibidos durante el intervalo
            bytes_sent_diff = net_io.bytes_sent - initial_net_io.bytes_sent
            bytes_recv_diff = net_io.bytes_recv - initial_net_io.bytes_recv

            # Cálculo de la velocidad en bytes por segundo
            upload_speed_bps = bytes_sent_diff / interval
            download_speed_bps = bytes_recv_diff / interval

            # Conversión de la velocidad a KB/s (1 KB = 1024 bytes)
            upload_speed_kbps = upload_speed_bps / 1024
            download_speed_kbps = download_speed_bps / 1024

            # Se actualizan los totales acumulados (convertidos a KB)
            cumulative_upload += bytes_sent_diff / 1024
            cumulative_download += bytes_recv_diff / 1024

            # Se imprime en consola la velocidad actual y los totales acumulados
            print(f"Subida: {upload_speed_kbps:.2f} KB/s | Bajada: {download_speed_kbps:.2f} KB/s | Acumulado: {cumulative_upload:.2f} KB subidos, {cumulative_download:.2f} KB bajados")

            # Si se habilitó el registro en CSV, se escribe la fila correspondiente
            if csv_writer:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                csv_writer.writerow([timestamp,
                                     f"{upload_speed_kbps:.2f}",
                                     f"{download_speed_kbps:.2f}",
                                     f"{cumulative_upload:.2f}",
                                     f"{cumulative_download:.2f}"])
                csv_file.flush()  # Se fuerza la escritura en el disco

            # Se actualizan las estadísticas iniciales para el próximo ciclo
            initial_net_io = net_io

            # Se espera el intervalo especificado antes de la siguiente medición
            time.sleep(interval)
    except KeyboardInterrupt:
        # Se maneja la interrupción del usuario con Ctrl+C
        print("\nMonitoreo detenido por el usuario.")
    finally:
        # Se cierra el archivo CSV si estaba abierto
        if csv_file:
            csv_file.close()

if __name__ == "__main__":
    # Configuración de los argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Monitorea el uso del ancho de banda de la red y opcionalmente registra los resultados en un archivo CSV.")
    parser.add_argument("--interval", type=float, default=1, help="Intervalo de tiempo entre mediciones en segundos (por defecto: 1)")
    parser.add_argument("--duration", type=float, default=None, help="Duración total del monitoreo en segundos (por defecto: indefinido hasta Ctrl+C)")
    parser.add_argument("--log", type=str, default=None, help="Ruta del archivo CSV para guardar los resultados (por defecto: sin log)")

    args = parser.parse_args()

    # Se inicia el monitoreo con los parámetros proporcionados
    get_network_usage(interval=args.interval, duration=args.duration, log_file=args.log)
