import network
from umqtt.simple import MQTTClient
from machine import Pin, PWM, reset
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.19.169"
MQTT_CLIENT_ID = "KY006_BUZZER"
MQTT_TOPIC_BUZZER = "utng/buzzer"
MQTT_PORT = 1883

# Configuración del buzzer pasivo KY-006
BUZZER_PIN = 4
buzzer = PWM(Pin(BUZZER_PIN))

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
    client.publish(MQTT_TOPIC_BUZZER, json.dumps({"status": "online"}))
    return client

# Función para reproducir un beep
def beep_buzzer(duracion=0.5, frecuencia=1000):
    buzzer.freq(frecuencia)
    buzzer.duty(512)  # 50% duty cycle
    time.sleep(duracion)
    buzzer.duty(0)

# Setup inicial
try:
    conectar_wifi()
    client = conectar_broker()
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    time.sleep(5)
    reset()  # Reinicia si falla algo al inicio

# Bucle principal: sonar cada 2 segundos y enviar mensaje MQTT
while True:
    try:
        beep_buzzer()
        client.publish(MQTT_TOPIC_BUZZER, json.dumps({"buzzer": "beep"}))
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error en el bucle: {e}")
        time.sleep(2)
        reset()  # Reinicia si hay un fallo grave

