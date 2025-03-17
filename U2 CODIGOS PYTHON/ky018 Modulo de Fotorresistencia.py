import network
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.19.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY018_LightSensor"
MQTT_TOPIC_PUBLISH = "utng/sensor"  # Tema para publicar datos del sensor
MQTT_PORT = 1883

# Configuración del KY-018 (Fotorresistencia)
SENSOR_PIN = 34  # GPIO conectado al pin de señal del KY-018 (debe ser un pin ADC)
sensor = ADC(Pin(SENSOR_PIN))  # Configurar como entrada analógica
sensor.atten(ADC.ATTN_11DB)  # Configurar atenuación para un rango de 0-3.3V (0-4095)

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

# Función para leer el nivel de luz del sensor
def read_light_intensity():
    light_value = sensor.read()  # Leer el valor analógico (0-4095)
    return light_value

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
        # Leer el nivel de luz del sensor
        light_intensity = read_light_intensity()
        
        # Imprimir datos en la consola
        print(f"Nivel de luz: {light_intensity}")
        
        # Publicar datos en el broker MQTT
        mqtt_message = json.dumps({
            "light_intensity": light_intensity
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(1)  # Esperar 1 segundo entre mediciones