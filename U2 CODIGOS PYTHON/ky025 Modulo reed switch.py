from umqtt.simple import MQTTClient
import network
from machine import Pin
import time
import json

# WiFi Configuration
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# MQTT Configuration
MQTT_BROKER = "192.168.202.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY025_ReedSwitch"
MQTT_TOPIC_PUBLISH = "utng/ky025"  # Topic to publish reed switch data
MQTT_PORT = 1883

# KY-025 Reed Switch Configuration
SENSOR_PIN = 14  # GPIO connected to the DIGITAL output pin of KY-025
sensor = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Configure as digital input with pull-up

# Function to connect to WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi Conectada!")
    print("IP:", sta_if.ifconfig()[0])

# Function to connect to MQTT broker
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC_PUBLISH}")
    return client

# Function to read the KY-025 Reed Switch state
def read_reed_switch():
    try:
        # Read sensor state (0 = magnetic field detected/switch closed, 1 = not detected/switch open)
        state = sensor.value()
        return "closed" if state == 0 else "open"
    except Exception as e:
        print(f"Error al leer el sensor: {e}")
        return None

# Connect to WiFi and MQTT
try:
    conectar_wifi()
    client = conectar_broker()
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    import machine
    machine.reset()

# Main loop
while True:
    try:
        # Read the reed switch state
        switch_state = read_reed_switch()
        
        if switch_state is not None:
            # Print data to console
            print(f"Estado del Reed Switch: {switch_state}")
            
            # Create a JSON message with the reed switch state
            mqtt_message = json.dumps({
                "switch_state": switch_state,
                "timestamp": time.time()
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudo leer el estado del Reed Switch.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        try:
            client.disconnect()
        except:
            pass
        time.sleep(5)
        import machine
        machine.reset()
    
    # Small pause before the next iteration
    time.sleep(0.5)  # Wait 500 ms between measurements