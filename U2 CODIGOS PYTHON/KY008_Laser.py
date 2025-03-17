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
MQTT_CLIENT_ID = "KY012_Buzzer"
MQTT_TOPIC_SUBSCRIBE = "utng/buzzer"  # Tema para recibir comandos
MQTT_TOPIC_PUBLISH = "utng/buzzer"  # Tema para publicar estados
MQTT_PORT = 1883

# Configuración del KY-012 (Buzzer Activo)
BUZZER_PIN = 4  # GPIO conectado al buzzer activo
buzzer = Pin(BUZZER_PIN, Pin.OUT)  # Configurar como salida digital

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

# Función para cambiar el estado del buzzer
def set_buzzer_state(state):
    buzzer.value(state)  # Enciende/Apaga el buzzer
    return "ON" if state == 1 else "OFF"

# Callback para manejar mensajes MQTT
def mqtt_callback(topic, msg):
    print(f"Mensaje recibido: {msg.decode()} en el tema: {topic.decode()}")
    try:
        # Parsear el mensaje como un string
        command = msg.decode().upper()
        if command == "ON":
            buzzer_state = set_buzzer_state(1)  # Encender el buzzer
        elif command == "OFF":
            buzzer_state = set_buzzer_state(0)  # Apagar el buzzer
        else:
            print("Comando no reconocido")
            return
        
        # Publicar el estado actual del buzzer
        estado = {"buzzer": buzzer_state}
        client.publish(MQTT_TOPIC_PUBLISH, json.dumps(estado))
        print(f"Estado del Buzzer publicado: {estado}")
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    client = conectar_broker()

    # Suscribirse al tema MQTT
    client.set_callback(mqtt_callback)
    client.subscribe(MQTT_TOPIC_SUBSCRIBE)

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
        # Verificar si hay nuevos mensajes MQTT
        client.check_msg()
        
        # Pequeña pausa antes de la siguiente iteración
        time.sleep(0.1)

    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()