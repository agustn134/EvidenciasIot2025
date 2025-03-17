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
MQTT_CLIENT_ID = "KY021_MagneticSwitch"
MQTT_TOPIC_PUBLISH = "utng/ky021"  
MQTT_PORT = 1883

# Configuración del KY-021 (Interruptor Magnético)
SENSOR_PIN = 4  # GPIO conectado al pin de señal del KY-021
sensor = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Configurar como entrada con pull-up

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

# Función para leer el estado del KY-021
def read_switch_state():
    try:
        # Leer el estado del sensor (0 = imán cerca, 1 = imán lejos)
        state = sensor.value()
        return "closed" if state == 0 else "open"
    except Exception as e:
        print(f"Error al leer el sensor: {e}")
        return None

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
        # Leer el estado del interruptor magnético
        switch_state = read_switch_state()
        
        if switch_state is not None:
            # Imprimir datos en la consola
            print(f"Estado del interruptor: {switch_state}")
            
            # Crear un mensaje JSON con el estado del sensor
            mqtt_message = json.dumps({
                "switch_state": switch_state
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudo leer el estado del interruptor.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(2)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(1)  # Esperar 1 segundo entre mediciones