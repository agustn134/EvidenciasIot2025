import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.19.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "utng/sensor"
MQTT_PORT = 1883

# Configuración del sensor de mercurio
SENSOR_PIN = 5  # GPIO donde está conectado el sensor
sensor = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Entrada con pull-up

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi Conectada!")

# Función para conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
    return client

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_broker()

estado_anterior = sensor.value()  # Guardar el último estado del sensor

# Bucle principal
while True:
    estado_actual = sensor.value()  # Leer el sensor de mercurio
    mensaje = "Inclinado" if estado_actual == 0 else "Normal"

    # Mostrar en consola siempre
    print(f"Estado del sensor: {mensaje}")

    # Si el estado cambió, enviamos una actualización a MQTT
    if estado_actual != estado_anterior:
        client.publish(MQTT_TOPIC, mensaje)
        estado_anterior = estado_actual  # Actualizar estado anterior

    time.sleep(0.5)  # Pequeña pausa antes de la siguiente lectura