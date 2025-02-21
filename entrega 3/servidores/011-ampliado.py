import psutil      # Para obtener estadísticas del sistema y de red
import time        # Para manejar los intervalos y tiempos de espera
import argparse    # Para permitir la configuración vía argumentos de línea de comandos
import csv         # Para escribir las anomalías en un archivo CSV (opcional)

def get_network_usage(interval):
    """
    Mide el uso de red (subida y bajada) durante un intervalo dado.

    Parámetros:
        interval (float): Tiempo en segundos que se espera para calcular el uso.

    Retorna:
        tuple: (subida, descarga) en bytes/segundo.
    """
    initial_net_io = psutil.net_io_counters()
    time.sleep(interval)
    net_io = psutil.net_io_counters()
    subida = (net_io.bytes_sent - initial_net_io.bytes_sent) / interval
    descarga = (net_io.bytes_recv - initial_net_io.bytes_recv) / interval
    return subida, descarga

def measure_baseline(interval, baseline_count):
    """
    Calcula los valores promedio (baseline) de subida y bajada a lo largo de 'baseline_count'
    mediciones, usando el intervalo definido.

    Parámetros:
        interval (float): Tiempo en segundos entre mediciones.
        baseline_count (int): Número de mediciones para calcular el baseline.

    Retorna:
        tuple: (baseline_subida, baseline_descarga)
    """
    total_subida = 0
    total_descarga = 0
    print("Empezamos el cálculo de valores normales (baseline)...")
    for _ in range(baseline_count):
        s, d = get_network_usage(interval)
        total_subida += s
        total_descarga += d
        print(f"Medición {_+1}/{baseline_count} -> Subida: {s:.2f} bytes/s, Descarga: {d:.2f} bytes/s")
    baseline_subida = total_subida / baseline_count
    baseline_descarga = total_descarga / baseline_count
    print(f"\nValores normales: Subida={baseline_subida:.2f} bytes/s, Descarga={baseline_descarga:.2f} bytes/s\n")
    return baseline_subida, baseline_descarga

def monitor_network(interval, baseline_subida, baseline_descarga, threshold, duration=None, log_file=None):
    """
    Monitorea en tiempo real el uso de red comparándolo con el baseline. Si la velocidad de
    subida o bajada supera el baseline multiplicado por 'threshold', se considera que hay una anomalía.

    Parámetros:
        interval (float): Intervalo de tiempo en segundos para las mediciones.
        baseline_subida (float): Valor de referencia para la velocidad de subida (bytes/s).
        baseline_descarga (float): Valor de referencia para la velocidad de bajada (bytes/s).
        threshold (float): Factor multiplicador para detectar anomalías.
        duration (float, opcional): Duración total del monitoreo en segundos. Si es None, se ejecuta indefinidamente.
        log_file (str, opcional): Ruta al archivo CSV para registrar las anomalías.
    """
    # Inicialización para el registro de anomalías
    anomaly_count = 0
    sum_anomaly_upload = 0
    sum_anomaly_download = 0

    if log_file:
        try:
            csv_file = open(log_file, mode='w', newline='')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Timestamp", "Subida (bytes/s)", "Descarga (bytes/s)"])
        except Exception as e:
            print(f"Error al abrir el archivo de log: {e}")
            csv_file = None
            csv_writer = None
    else:
        csv_file = None
        csv_writer = None

    print("Ahora comenzamos la toma de datos en tiempo real...")
    start_time = time.time()
    previous_net_io = psutil.net_io_counters()

    try:
        while True:
            current_time = time.time()
            # Si se define una duración, finalizamos al alcanzarla
            if duration is not None and (current_time - start_time) >= duration:
                print("Duración de monitoreo alcanzada.")
                break

            current_net_io = psutil.net_io_counters()
            nuevasubida = (current_net_io.bytes_sent - previous_net_io.bytes_sent) / interval
            nuevadescarga = (current_net_io.bytes_recv - previous_net_io.bytes_recv) / interval

            # Actualizamos el contador previo para la siguiente medición
            previous_net_io = current_net_io

            # Verificamos si se supera el umbral en alguna dirección
            if nuevasubida > baseline_subida * threshold or nuevadescarga > baseline_descarga * threshold:
                print(f"Anomalía detectada: Subida={nuevasubida:.2f} bytes/s, Descarga={nuevadescarga:.2f} bytes/s")
                anomaly_count += 1
                sum_anomaly_upload += nuevasubida
                sum_anomaly_download += nuevadescarga

                # Se registra la anomalía en el archivo CSV (si se especificó)
                if csv_writer:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    csv_writer.writerow([timestamp, f"{nuevasubida:.2f}", f"{nuevadescarga:.2f}"])
                    csv_file.flush()
            else:
                print(f"Normal: Subida={nuevasubida:.2f} bytes/s, Descarga={nuevadescarga:.2f} bytes/s")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
    finally:
        if csv_file:
            csv_file.close()

    # Imprimir resumen del monitoreo
    if anomaly_count > 0:
        avg_anomaly_upload = sum_anomaly_upload / anomaly_count
        avg_anomaly_download = sum_anomaly_download / anomaly_count
    else:
        avg_anomaly_upload = avg_anomaly_download = 0

    print("\n--- Resumen de Anomalías ---")
    print(f"Total de anomalías detectadas: {anomaly_count}")
    if anomaly_count:
        print(f"Promedio de subida en anomalías: {avg_anomaly_upload:.2f} bytes/s")
        print(f"Promedio de descarga en anomalías: {avg_anomaly_download:.2f} bytes/s")
    print("-----------------------------")

def main():
    # Configuración de argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="Monitorea la red comparando el uso actual con un baseline y detecta anomalías."
    )
    parser.add_argument("--interval", type=float, default=1,
                        help="Intervalo entre mediciones en segundos (por defecto: 1)")
    parser.add_argument("--baseline_count", type=int, default=10,
                        help="Número de mediciones para calcular el baseline (por defecto: 10)")
    parser.add_argument("--threshold", type=float, default=5.0,
                        help="Factor multiplicador para detectar anomalías (por defecto: 5)")
    parser.add_argument("--duration", type=float, default=None,
                        help="Duración total del monitoreo en segundos (por defecto: indefinido)")
    parser.add_argument("--log", type=str, default=None,
                        help="Ruta al archivo CSV para registrar anomalías (por ejemplo: anomalies.csv)")
    
    args = parser.parse_args()

    # Cálculo del baseline de red
    baseline_subida, baseline_descarga = measure_baseline(args.interval, args.baseline_count)

    # Inicio del monitoreo en tiempo real
    monitor_network(args.interval, baseline_subida, baseline_descarga,
                    args.threshold, args.duration, args.log)

if __name__ == "__main__":
    main()
