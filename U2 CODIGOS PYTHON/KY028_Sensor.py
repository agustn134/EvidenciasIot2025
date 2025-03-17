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
MQTT_CLIENT_ID = "KY028_Sensor"
MQTT_TOPIC_PUBLISH = "utng/sensor"  # Tema para publicar datos del sensor
MQTT_PORT = 1883

# Configuración del KY-028 (Sensor de temperatura)
TEMP_ANALOG_PIN = 34  # GPIO para la salida analógica del KY-028
TEMP_DIGITAL_PIN = 35  # GPIO para la salida digital del KY-028

# Configurar pines
temp_analog = ADC(Pin(TEMP_ANALOG_PIN))  # Entrada analógica
temp_analog.atten(ADC.ATTN_11DB)  # Configurar rango de 0-3.3V
temp_digital = Pin(TEMP_DIGITAL_PIN, Pin.IN)  # Entrada digital

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

# Función para leer la temperatura analógica
def read_temp_analog():
    raw_value = temp_analog.read()  # Leer valor crudo (0-4095)
    voltage = raw_value * 3.3 / 4095  # Convertir a voltaje (0-3.3V)
    temperature = (voltage - 0.5) * 100  # Fórmula aproximada para convertir a °C
    return temperature

# Función para leer la salida digital del sensor
def read_temp_digital():
    return temp_digital.value()  # Devuelve 0 o 1

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
        # Leer datos del sensor KY-028
        analog_temp = read_temp_analog()  # Temperatura analógica en °C
        digital_state = read_temp_digital()  # Estado digital (0 o 1)

        # Imprimir datos en la consola
        print(f"Temperatura: {analog_temp:.2f}°C, Estado digital: {digital_state}")

        # Publicar datos en el broker MQTT
        mqtt_message = json.dumps({
            "temperature": round(analog_temp, 2),
            "digital_state": digital_state
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)

    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()

    # Pequeña pausa antes de la siguiente iteración
    time.sleep(2)