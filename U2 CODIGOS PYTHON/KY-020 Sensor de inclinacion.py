import network
from umqtt.simple import MQTTClient
from machine import Pin
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.202.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY020_TiltSensor"
MQTT_TOPIC_PUBLISH = "sensor/inclinacion"  # Tema para publicar datos del sensor
MQTT_PORT = 1883

# Configuración del KY-020 (Sensor de Inclinación)
SENSOR_PIN = 14  # GPIO conectado al pin de señal del KY-020
sensor = Pin(SENSOR_PIN, Pin.IN)  # Configurar como entrada digital

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
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC_PUBLISH}")
    return client

# Función para leer el estado del sensor KY-020
def read_tilt_sensor():
    return sensor.value()  # Devuelve 0 o 1 dependiendo del estado del sensor

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    client = conectar_broker()
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    machine.reset()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor
        tilt_state = read_tilt_sensor()
        
        # Imprimir datos en la consola
        if tilt_state == 1:
            print("Sensor inclinado")
        else:
            print("Sensor en posición vertical")
        
        # Crear un mensaje JSON con el estado del sensor
        mqtt_message = json.dumps({
            "tilt_state": tilt_state
        })
        
        # Publicar el mensaje JSON en el broker MQTT
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(0.5)  # Esperar 0.5 segundos entre mediciones