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
MQTT_CLIENT_ID = "KY004_PushButton"
MQTT_TOPIC_PUBLISH = "utng/sensor"  # Tema para publicar datos del botón
MQTT_PORT = 1883

# Configuración del KY-004 (Push Botón)
BUTTON_PIN = 5  # GPIO conectado al pin de señal del KY-004
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)  # Configurar como entrada digital con resistencia pull-up

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

# Variables para la detección de flancos
last_state = 1  # Estado inicial del botón (no presionado)

# Bucle principal
try:
    conectar_wifi()
    client = conectar_broker()
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    machine.reset()

while True:
    try:
        # Leer el estado actual del botón
        current_state = button.value()
        
        # Detectar cambio de estado (flanco)
        if current_state != last_state:
            # Actualizar el estado anterior
            last_state = current_state
            
            # Determinar el mensaje según el estado del botón
            if current_state == 0:  # Botón presionado
                message = "BotonPresionado"
                print("Botón presionado")
            else:  # Botón no presionado
                message = "BotonNoPresionado"
                print("Botón no presionado")
            
            # Publicar datos en el broker MQTT como una cadena JSON
            mqtt_message = json.dumps({
                "mensaje": message
            })
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        
        # Pequeña pausa antes de la siguiente iteración
        time.sleep(0.1)
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()