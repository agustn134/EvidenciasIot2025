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
MQTT_CLIENT_ID = "KY029_BicolorLED"
MQTT_TOPIC_PUBLISH = "utng/ky029"  # Tema para publicar los datos del LED bicolor
MQTT_PORT = 1883

# Configuración del KY-029 (Módulo LED 2 colores 3mm)
# Normalmente un LED bicolor tiene dos pines de control
RED_PIN = 12    # GPIO para el color rojo
GREEN_PIN = 14  # GPIO para el color verde

# Configurar los pines como salidas
led_red = Pin(RED_PIN, Pin.OUT)
led_green = Pin(GREEN_PIN, Pin.OUT)

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
def set_led_color(color):
    if color == "red":
        led_red.value(1)
        led_green.value(0)
    elif color == "green":
        led_red.value(0)
        led_green.value(1)
    elif color == "yellow":  # Ambos LEDs encendidos pueden dar una apariencia amarillenta
        led_red.value(1)
        led_green.value(1)
    else:  # off - ambos apagados
        led_red.value(0)
        led_green.value(0)
    
    return color

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    client = conectar_broker()
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    import machine
    machine.reset()

# Estado inicial
current_color = "off"
color_sequence = ["red", "green", "yellow", "off"]
color_index = 0

# Bucle principal
while True:
    try:
        # Cambiar el color del LED en secuencia
        color_index = (color_index + 1) % len(color_sequence)
        current_color = color_sequence[color_index]
        
        # Configurar el LED con el nuevo color
        set_led_color(current_color)
        
        # Imprimir datos en la consola
        print(f"Color del LED: {current_color}")
        
        # Crear un mensaje JSON con el estado del LED
        mqtt_message = json.dumps({
            "led_color": current_color,
            "timestamp": time.time()
        })
        
        print(f"Mensaje MQTT enviado: {mqtt_message}")
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        import machine
        machine.reset()
    
    # Esperar antes de cambiar al siguiente color
    time.sleep(2)  # Esperar 2 segundos entre cambios de color