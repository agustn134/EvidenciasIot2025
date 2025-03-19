from machine import Pin
import time

# Configuración del KY-005 (Emisor Infrarrojo)
IR_PIN = 14  # GPIO conectado al pin del KY-005
ir_led = Pin(IR_PIN, Pin.OUT)  # Configurar como salida digital

# Frecuencia de modulación (38 kHz)
FREQ = 38000  # 38 kHz
PERIOD_US = 1_000_000 // FREQ  # Periodo en microsegundos

# Función para enviar una señal modulada
def send_ir_signal(on_time_ms, off_time_ms):
    """
    Envía una señal infrarroja modulada.
    :param on_time_ms: Tiempo en milisegundos que la señal está activa.
    :param off_time_ms: Tiempo en milisegundos que la señal está inactiva.
    """
    # Calcular el número de ciclos para el tiempo "on"
    cycles_on = int((on_time_ms * 1000) // PERIOD_US)
    
    # Enviar la señal modulada
    for _ in range(cycles_on):
        ir_led.on()
        time.sleep_us(PERIOD_US // 2)  # Encendido durante medio ciclo
        ir_led.off()
        time.sleep_us(PERIOD_US // 2)  # Apagado durante medio ciclo
    
    # Esperar el tiempo "off"
    time.sleep_ms(off_time_ms)

# Ejemplo de uso: Simular un patrón de señal IR
def send_ir_command():
    """
    Envía un comando IR simulado con un patrón específico.
    """
    print("Enviando señal IR...")
    # Patrón de ejemplo: Encender durante 10 ms, apagar durante 20 ms, repetir
    for _ in range(5):  # Repetir el patrón 5 veces
        send_ir_signal(on_time_ms=10, off_time_ms=20)
    print("Señal IR enviada.")

# Bucle principal
while True:
    try:
        # Enviar un comando IR cada 5 segundos
        send_ir_command()
        time.sleep(5)
    except KeyboardInterrupt:
        print("Interrupción detectada. Deteniendo...")
        break