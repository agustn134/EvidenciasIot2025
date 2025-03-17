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
MQTT_CLIENT_ID = "KY001_Temperatura"
MQTT_TOPIC_PUBLISH = "utng/temp"  # Tema para publicar datos de temperatura
MQTT_PORT = 1883

# Configuración del KY-001 (Sensor de Temperatura)
TEMP_PIN = 34  # GPIO conectado al sensor
temp_sensor = ADC(Pin(TEMP_PIN))  # Configurar como entrada analógica

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

# Función para leer la temperatura
def read_temperature():
    # Leer el valor analógico del sensor
    raw_value = temp_sensor.read()
    
    # Convertir el valor analógico a voltaje (ESP32 ADC 12 bits)
    voltage = raw_value * 3.3 / 4095
    
    # Convertir el voltaje a temperatura (ajustar según calibración del sensor)
    temperature = (voltage - 0.5) * 100  # Fórmula aproximada para termistores
    
    return round(temperature, 2)  # Redondear a 2 decimales

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
        # Leer la temperatura
        temperature = read_temperature()
        
        # Publicar datos en el broker MQTT
        mqtt_message = json.dumps({
            "temperatura": temperature
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        print(f"Temperatura: {temperature} °C")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(2)