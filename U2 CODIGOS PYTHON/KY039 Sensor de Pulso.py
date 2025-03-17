import network
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.226.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY039_HeartRate"
MQTT_TOPIC_PUBLISH = "utng/ky039"  # Tema para publicar el ritmo cardíaco
MQTT_PORT = 1883

# Configuración del sensor KY-039
SENSOR_PIN = 34  # GPIO conectado al sensor KY-039 (ADC)
adc = ADC(Pin(SENSOR_PIN))
adc.atten(ADC.ATTN_11DB)  # Configurar atenuación para rango completo (0-3.3V)

# Variables para cálculo del ritmo cardíaco
THRESHOLD = 1000  # Umbral para detectar picos (ajustar según sea necesario)
last_time = 0
beat_count = 0
bpm = 0

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

# Función para calcular el ritmo cardíaco
def calculate_heart_rate(current_time):
    global last_time, beat_count, bpm
    if current_time - last_time > 0:
        bpm = int((beat_count / (current_time - last_time)) * 60)
        last_time = current_time
        beat_count = 0
    return bpm

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    client = conectar_broker()
    time.sleep(1)
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    machine.reset()

# Bucle principal
last_peak_time = time.ticks_ms()
while True:
    try:
        # Leer el valor del sensor
        raw_value = adc.read()
        print(f"Valor del sensor: {raw_value}")
        
        # Detectar picos en el flujo sanguíneo
        if raw_value > THRESHOLD:
            current_time = time.ticks_ms()
            if current_time - last_peak_time > 200:  # Evitar múltiples detecciones en un solo pico
                beat_count += 1
                last_peak_time = current_time
            
            # Calcular el ritmo cardíaco
            bpm = calculate_heart_rate(time.ticks_diff(current_time, last_peak_time) / 1000)
            
            # Publicar el ritmo cardíaco en MQTT
            mqtt_message = json.dumps({
                "heart_rate": bpm,
                "sensor_value": raw_value
            })
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
            print(f"Ritmo cardíaco: {bpm} BPM, Valor del sensor: {raw_value}")
        
        time.sleep(0.1)  # Pequeño delay para evitar lecturas demasiado rápidas
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()