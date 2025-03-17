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
MQTT_CLIENT_ID = "KY011_LED_2Colores"
MQTT_TOPIC_PUBLISH = "utng/led"  # Tema para publicar estados del LED
MQTT_PORT = 1883

# Configuración del KY-011 (LED 2 Colores)
RED_PIN = 5  # GPIO conectado al LED rojo
GREEN_PIN = 4  # GPIO conectado al LED verde

red_led = Pin(RED_PIN, Pin.OUT)  # Configurar como salida digital
green_led = Pin(GREEN_PIN, Pin.OUT)  # Configurar como salida digital

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

# Función para cambiar el estado de los LEDs
def set_led_state(red_state, green_state):
    print(f"Cambiando estado: Rojo={red_state}, Verde={green_state}")
    red_led.value(red_state)  # Enciende/Apaga el LED rojo
    green_led.value(green_state)  # Enciende/Apaga el LED verde

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    client = conectar_broker()

    # Apagar ambos LEDs al inicio
    set_led_state(0, 0)
    time.sleep(1)

except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    machine.reset()

# Bucle principal
while True:
    try:
        # Alternar estados de los LEDs
        set_led_state(1, 0)  # Encender solo el LED rojo
        mqtt_message = json.dumps({
            "rojo": "ON",
            "verde": "OFF"
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        print("LED Rojo: ON, LED Verde: OFF")
        time.sleep(1)

        set_led_state(0, 1)  # Encender solo el LED verde
        mqtt_message = json.dumps({
            "rojo": "OFF",
            "verde": "ON"
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        print("LED Rojo: OFF, LED Verde: ON")
        time.sleep(1)

        set_led_state(1, 1)  # Encender ambos LEDs (mezcla de colores)
        mqtt_message = json.dumps({
            "rojo": "ON",
            "verde": "ON"
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        print("LED Rojo: ON, LED Verde: ON")
        time.sleep(1)

        set_led_state(0, 0)  # Apagar ambos LEDs
        mqtt_message = json.dumps({
            "rojo": "OFF",
            "verde": "OFF"
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        print("LED Rojo: OFF, LED Verde: OFF")
        time.sleep(1)

    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()