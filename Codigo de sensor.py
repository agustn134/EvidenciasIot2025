from machine import Pin
import time
import network
import urequests
from umqtt.simple import MQTTClient

# Pines del sensor HR-SR04
TRIGGER_PIN = 18  # Pin GPIO para el trigger
ECHO_PIN = 5   # Pin GPIO para el echo

# Configuración de Wi-Fi
SSID = 'S20 Ultra'
PASSWORD = '123456789'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.29.169'  # IP del Raspberry Pi con Node-RED
MQTT_TOPIC = 'sensor/distance'

# Inicializar pines
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print('Conexión WiFi establecida:', wlan.ifconfig())

def get_distance():
    # Generar pulso de trigger
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    # Medir la duración del pulso de retorno
    while echo.value() == 0:
        pass
    start_time = time.ticks_us()

    while echo.value() == 1:
        pass
    end_time = time.ticks_us()

    # Calcular distancia en cm
    duration = time.ticks_diff(end_time, start_time)
    distance = (duration / 2) * 0.0343
    return round(distance, 2)

def publish_distance(client):
    distance = get_distance()
    print('Distancia:', distance, 'cm')
    client.publish(MQTT_TOPIC, str(distance))

def main():
    connect_wifi()
    client = MQTTClient('esp32_client', MQTT_BROKER)
    client.connect()
    print('Conectado al broker MQTT')

    try:
        while True:
            publish_distance(client)
            time.sleep(2)  # Publicar cada 2 segundos
    except KeyboardInterrupt:
        print('Desconectando...')
        client.disconnect()

if __name__ == '__main__':
    main()
