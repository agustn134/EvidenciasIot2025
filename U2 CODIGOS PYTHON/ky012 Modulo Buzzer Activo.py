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
MQTT_CLIENT_ID = "KY005_Buzzer"
MQTT_TOPIC_PUBLISH = "utng/buzzer"  # Tema para publicar estados del buzzer
MQTT_PORT = 1883

# Configuración de pines
BUZZER_PIN = 5  # GPIO conectado al Buzzer Activo
IR_SENSOR_PIN = 4  # GPIO conectado al Sensor Infrarrojo KY-005

# Configurar el Buzzer como salida
buzzer = Pin(BUZZER_PIN, Pin.OUT)
# Configurar el Sensor Infrarrojo como entrada
ir_sensor = Pin(IR_SENSOR_PIN, Pin.IN)

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

# Función para cambiar el estado del buzzer
def set_buzzer_state(state):
    buzzer.value(state)  # Enciende/Apaga el buzzer
    return "ON" if state == 1 else "OFF"

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    client = conectar_broker()
    # Apagar el buzzer al inicio
    set_buzzer_state(0)
    time.sleep(1)
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    machine.reset()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor infrarrojo
        ir_state = ir_sensor.value()  # 1 si no detecta, 0 si detecta
        
        if ir_state == 0:  # Si el sensor detecta algo
            buzzer_state = set_buzzer_state(1)  # Encender el buzzer
        else:
            buzzer_state = set_buzzer_state(0)  # Apagar el buzzer
        
        # Publicar el estado del buzzer en MQTT
        mqtt_message = json.dumps({
            "buzzer": buzzer_state,
            "sensor": "DETECTED" if ir_state == 0 else "NOT DETECTED"
        })
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        print(f"Buzzer: {buzzer_state}, Sensor: {'DETECTED' if ir_state == 0 else 'NOT DETECTED'}")
        
        time.sleep(0.5)  # Pequeño delay para evitar lecturas rápidas
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()