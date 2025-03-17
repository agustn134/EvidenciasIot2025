import network
from umqtt.simple import MQTTClient
from machine import Pin
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.19.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY10_PhotoInterruptor"
MQTT_TOPIC_PUBLISH = "utng/sensor"  # Mismo tema para publicar datos del sensor
MQTT_PORT = 1883

# Configuración del KY-10 (Foto-interruptor)
SENSOR_PIN = 14  # GPIO conectado al pin de señal del KY-10
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

# Función para leer el estado del sensor
def read_photo_interruptor():
    return sensor.value()  # Devuelve 0 o 1

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
        state = read_photo_interruptor()
        
        # Imprimir datos en la consola
        if state == 1:
            print("Haz de luz detectado (Sin interrupción)")
        else:
            print("Haz de luz interrumpido (Objeto detectado)")
        
        # Publicar datos en el broker MQTT
        mqtt_message = json.dumps({
            "state": state
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(0.5)