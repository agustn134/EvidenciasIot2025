import network
from umqtt.simple import MQTTClient
from machine import Pin, reset
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.19.169"
MQTT_CLIENT_ID = "KY022_SENSOR"
MQTT_TOPIC_IR = "utng/sensor22"
MQTT_PORT = 1883

# Configuración del sensor KY-022 (receptor infrarrojo)
IR_PIN = 5
ir_sensor = Pin(IR_PIN, Pin.IN)

# Estado anterior (para detectar cambios)
last_ir_state = ir_sensor.value()

# Conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        time.sleep(0.5)
        print(".", end="")
    print("\n✅ WiFi Conectada!")

# Conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print(f"✅ Conectado a MQTT Broker: {MQTT_BROKER}")
    client.publish(MQTT_TOPIC_IR, json.dumps({"status": "online"}))
    return client

# Leer el estado del sensor infrarrojo y avisar a MQTT si cambia
def verificar_sensor_ir(client):
    global last_ir_state
    ir_state = ir_sensor.value()

    if ir_state != last_ir_state:
        last_ir_state = ir_state

        if ir_state == 0:  # Señal detectada
            print("🔴 Señal infrarroja DETECTADA")
            client.publish(MQTT_TOPIC_IR, json.dumps({"ir": "DETECTED"}))
        else:  # No hay señal
            print("⚪ Sin señal infrarroja")
            client.publish(MQTT_TOPIC_IR, json.dumps({"ir": "NOT_DETECTED"}))

# Setup inicial
try:
    conectar_wifi()
    client = conectar_broker()
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    time.sleep(5)
    reset()

# Bucle principal
while True:
    try:
        verificar_sensor_ir(client)
        time.sleep(0.5)  # Revisar el sensor cada medio segundo
    except Exception as e:
        print(f"❌ Error en el bucle: {e}")
        time.sleep(2)
        reset()  # Reinicia si hay un fallo grave
