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
MQTT_CLIENT_ID = "KY024_MagneticField"
MQTT_TOPIC_PUBLISH = "utng/ky024"  # Tema para publicar los datos del campo magnético
MQTT_PORT = 1883

# Configuración del KY-024 (Sensor de Campo Magnético)
SENSOR_PIN = 4  # GPIO conectado al pin de señal DIGITAL del KY-024
sensor = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Configurar como entrada digital con pull-up

# Configuración del LED
LED_PIN = 15  # GPIO conectado al LED (en ESP32, GPIO2 es el LED integrado)
led = Pin(LED_PIN, Pin.OUT)  # Configurar el pin como salida

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

# Función para leer el estado del sensor KY-024
def read_magnetic_field():
    try:
        # Leer el estado del sensor (0 = campo magnético detectado, 1 = no detectado)
        state = sensor.value()
        return "detected" if state == 0 else "not_detected"
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
        # Leer el estado del campo magnético
        magnetic_state = read_magnetic_field()
        
        if magnetic_state is not None:
            # Imprimir datos en la consola
            print(f"Estado del campo magnético: {magnetic_state}")
            
            # Determinar si se debe encender o apagar el LED
            if magnetic_state == "detected":
                led.value(1)  # Encender el LED
                led_state = "ON"
            else:
                led.value(0)  # Apagar el LED
                led_state = "OFF"
            
            # Crear un mensaje JSON con el estado del campo magnético y el LED
            mqtt_message = json.dumps({
                "magnetic_state": magnetic_state,
                "led_state": led_state
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudo leer el estado del campo magnético.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(0.5)  # Esperar 500 ms entre mediciones