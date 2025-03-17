import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.202.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY019_Relay"
MQTT_TOPIC_SUBSCRIBE = "utng/relay/control"  # Tema para recibir comandos del relé
MQTT_TOPIC_PUBLISH = "utng/relay/status"     # Tema para publicar el estado del relé
MQTT_PORT = 1883

# Configuración del KY-019 (Módulo de Relé)
RELAY_PIN = 14  # GPIO conectado al pin IN del KY-019
relay = Pin(RELAY_PIN, Pin.OUT)  # Configurar el pin como salida

# Estado inicial del relé
relay_state = False  # False = Apagado, True = Encendido
relay.value(relay_state)  # Inicializar el relé en estado apagado

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
    client.set_callback(on_message)  # Configurar la función de callback para mensajes MQTT
    client.connect()
    client.subscribe(MQTT_TOPIC_SUBSCRIBE)  # Suscribirse al tema de control del relé
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC_SUBSCRIBE}")
    return client

# Función de callback para procesar mensajes MQTT
def on_message(topic, msg):
    global relay_state
    print(f"Mensaje recibido: {topic.decode()} => {msg.decode()}")
    
    if topic.decode() == MQTT_TOPIC_SUBSCRIBE:
        command = msg.decode().lower()
        if command == "on":
            relay_state = True
            relay.value(1)  # Encender el relé
            print("Relé encendido")
        elif command == "off":
            relay_state = False
            relay.value(0)  # Apagar el relé
            print("Relé apagado")
        
        # Crear el mensaje MQTT
        mqtt_message = "ON" if relay_state else "OFF"
        print(f"Mensaje MQTT enviado: {mqtt_message}")  # Imprimir el mensaje antes de publicarlo
        client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)  # Publicar el estado del relé

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
        # Verificar si hay nuevos mensajes MQTT
        client.check_msg()
        
        # Pequeña pausa antes de la siguiente iteración
        time.sleep(0.1)
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()