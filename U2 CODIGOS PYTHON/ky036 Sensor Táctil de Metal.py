import network
from umqtt.simple import MQTTClient
from machine import Pin
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.226.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY036_TouchSensor"
MQTT_TOPIC_PUBLISH = "utng/ky036"  # Tema para publicar estados del sensor táctil
MQTT_PORT = 1883

# Configuración de pines
TOUCH_SENSOR_PIN = 5  # GPIO conectado al sensor táctil KY-036
LED_PIN = 4  # GPIO conectado a un LED (opcional, para indicar detección)

# Configurar el sensor táctil como entrada
touch_sensor = Pin(TOUCH_SENSOR_PIN, Pin.IN)
# Configurar el LED como salida (opcional)
led = Pin(LED_PIN, Pin.OUT)

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

# Función para cambiar el estado del LED
def set_led_state(state):
    led.value(state)  # Enciende/Apaga el LED
    return "ON" if state == 1 else "OFF"

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    client = conectar_broker()
    # Apagar el LED al inicio
    set_led_state(0)
    time.sleep(1)
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    machine.reset()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor táctil
        touch_state = touch_sensor.value()  # 1 si se detecta toque, 0 si no
        
        if touch_state == 1:  # Si se detecta un toque
            led_state = set_led_state(1)  # Encender el LED
        else:
            led_state = set_led_state(0)  # Apagar el LED
        
        # Publicar el estado del sensor en MQTT
        mqtt_message = json.dumps({
            "touch": "DETECTED" if touch_state == 1 else "NOT DETECTED",
            "led": led_state
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        print(f"Toque: {'DETECTED' if touch_state == 1 else 'NOT DETECTED'}, LED: {led_state}")
        
        time.sleep(0.5)  # Pequeño delay para evitar lecturas rápidas
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(2)
        machine.reset()