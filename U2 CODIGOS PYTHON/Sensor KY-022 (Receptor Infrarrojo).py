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
MQTT_CLIENT_ID = "KY022_IRReceiver"
MQTT_TOPIC_PUBLISH = "utng/ky022"  # Tema para publicar los comandos IR recibidos
MQTT_PORT = 1883

# Configuración del KY-022 (Receptor IR)
IR_PIN = 4  # GPIO conectado al pin de señal del KY-022
ir_receiver = Pin(IR_PIN, Pin.IN)  # Configurar el receptor IR

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

# Función para leer señales IR
def read_ir_signal():
    try:
        # Leer el estado del receptor IR
        state = ir_receiver.value()  # Leer el valor del pin (0 o 1)
        return state
    except Exception as e:
        print(f"Error al leer el receptor IR: {e}")
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
        # Leer la señal IR
        ir_signal = read_ir_signal()
        
        if ir_signal is not None:
            # Imprimir datos en la consola
            print(f"Señal IR recibida: {ir_signal}")
            
            # Crear un mensaje JSON con los datos del receptor IR
            mqtt_message = json.dumps({
                "ir_signal": ir_signal
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se recibieron señales IR.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(0.1)  # Esperar 100 ms entre mediciones