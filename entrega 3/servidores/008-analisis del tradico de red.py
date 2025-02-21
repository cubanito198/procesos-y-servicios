import speedtest
import time

def measure_speeds():
    """
    Mide las velocidades de descarga y carga de la red usando speedtest-cli.
    También registra los resultados en un archivo de log para análisis posterior.
    """
    st = speedtest.Speedtest()  # Se espera que Speedtest esté disponible

    print("Buscando el mejor servidor...")
    st.get_best_server()

    print("Midiendo la velocidad de descarga...")
    download_start = time.time()
    download_speed = st.download()
    download_duration = time.time() - download_start
    download_speed_mbps = (download_speed / 8) / 1_000_000

    print("Midiendo la velocidad de carga...")
    upload_start = time.time()
    upload_speed = st.upload()
    upload_duration = time.time() - upload_start
    upload_speed_mbps = (upload_speed / 8) / 1_000_000

    print(f"Velocidad de descarga: {download_speed_mbps / download_duration:.2f} MB/s")
    print(f"Velocidad de carga: {upload_speed_mbps / upload_duration:.2f} MB/s")

    log_results(download_speed_mbps / download_duration, upload_speed_mbps / upload_duration)

def log_results(download_speed, upload_speed):
    """
    Registra los resultados de la prueba de velocidad en un archivo de log.
    """
    with open("speedtest_results.log", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Descarga: {download_speed:.2f} MB/s, Carga: {upload_speed:.2f} MB/s\n")
    print("✅ Los resultados se han registrado en 'speedtest_results.log'.")

if __name__ == "__main__":
    measure_speeds()
