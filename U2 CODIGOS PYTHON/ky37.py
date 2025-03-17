import network
from umqtt.simple import MQTTClient
from machine import Pin, ADC
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

# Configuración del sensor KY-037 (salida analógica)
SENSOR_PIN = 34  # GPIO donde está conectado el sensor (AO)
adc = ADC(Pin(SENSOR_PIN))  # Configurar el pin como entrada analógica
adc.atten(ADC.ATTN_11DB)  # Configurar el rango de voltaje (0-3.3V)

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

# Bucle principal
while True:
    # Leer el valor analógico del sensor (0-4095)
    valor_analogico = adc.read()
    
    # Publicar el valor en MQTT
    client.publish(MQTT_TOPIC, str(valor_analogico))
    
    # Mostrar en consola
    print(f"Valor analógico del sensor: {valor_analogico}")
    
    # Pequeña pausa antes de la siguiente lectura
    time.sleep(0.5)