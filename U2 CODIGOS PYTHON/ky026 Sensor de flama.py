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
MQTT_CLIENT_ID = "KY026_Flame"
MQTT_TOPIC_PUBLISH = "utng/ky026"  # Tema para publicar los datos del sensor de flama
MQTT_PORT = 1883

# Configuración del KY-026 (Sensor de Flama)
SENSOR_PIN = 14  # GPIO conectado al pin de señal DIGITAL del KY-026
sensor = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Configurar como entrada digital con pull-up

# Configuración del LED
LED_PIN = 12  # GPIO conectado al LED
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

# Función para leer el estado del sensor KY-026
def read_flame_sensor():
    try:
        # Leer el estado del sensor (0 = flama detectada, 1 = no detectada)
        # La lógica puede variar dependiendo de cómo esté configurado el módulo
        state = sensor.value()
        return "detectado" if state == 0 else "no_detectado"
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
    import machine
    machine.reset()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor de flama
        flame_state = read_flame_sensor()
        
        if flame_state is not None:
            # Imprimir datos en la consola
            print(f"Estado del sensor de flama: {flame_state}")
            
            # Determinar si se debe encender o apagar el LED
            if flame_state == "detectado":
                led.value(1)  # Encender el LED
                led_state = "ON"
            else:
                led.value(0)  # Apagar el LED
                led_state = "OFF"
            
            # Crear un mensaje JSON con el estado del sensor de flama y el LED
            mqtt_message = json.dumps({
                "flame_state": flame_state,
                "led_state": led_state
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudo leer el estado del sensor de flama.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        import machine
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(0.8)  # Esperar 500 ms entre mediciones