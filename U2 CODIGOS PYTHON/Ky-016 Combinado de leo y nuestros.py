import network
from umqtt.simple import MQTTClient
from machine import Pin, PWM
import time

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.19.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC_SUBSCRIBE = "utng/sensor"  # Tema para recibir comandos de color
MQTT_PORT = 1883

# Configuración del KY-016 (LED RGB)
RED_PIN = 25  # GPIO para el pin rojo
GREEN_PIN = 26  # GPIO para el pin verde
BLUE_PIN = 27  # GPIO para el pin azul

# Configurar PWM para cada pin del LED RGB
red_pwm = PWM(Pin(RED_PIN), freq=5000)
green_pwm = PWM(Pin(GREEN_PIN), freq=5000)
blue_pwm = PWM(Pin(BLUE_PIN), freq=5000)

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
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC_SUBSCRIBE}")
    return client

# Función para controlar el LED RGB
def set_rgb_color(red, green, blue):
    red_pwm.duty(int(red / 255 * 1023))  # Escalar valor de 0-255 a 0-1023
    green_pwm.duty(int(green / 255 * 1023))
    blue_pwm.duty(int(blue / 255 * 1023))

# Callback para manejar mensajes MQTT
def mqtt_callback(topic, msg):
    print(f"Mensaje recibido: {msg.decode()} en el tema: {topic.decode()}")
    try:
        # Parsear el mensaje como un diccionario JSON
        data = eval(msg.decode())  # Convertir string a diccionario
        red = data.get("red", 0)
        green = data.get("green", 0)
        blue = data.get("blue", 0)
        
        # Validar valores entre 0 y 255
        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))
        
        # Establecer el color del LED RGB
        set_rgb_color(red, green, blue)
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_broker()

# Suscribirse al tema MQTT
client.set_callback(mqtt_callback)
client.subscribe(MQTT_TOPIC_SUBSCRIBE)

# Bucle principal
while True:
    # Verificar si hay nuevos mensajes MQTT
    client.check_msg()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(0.1)
