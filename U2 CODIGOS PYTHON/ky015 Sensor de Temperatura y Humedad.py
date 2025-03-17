import network
from umqtt.simple import MQTTClient
from machine import Pin
import time
import json
import dht  # Biblioteca para el sensor DHT11/DHT22

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.202.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY015_TempHumidity"
MQTT_TOPIC_PUBLISH = "utng/humedad"  # Tema para publicar datos del sensor
MQTT_PORT = 1883

# Configuración del KY-015 (Sensor de Temperatura y Humedad)
SENSOR_PIN = 14  # GPIO conectado al pin de señal del KY-015
sensor = dht.DHT11(Pin(SENSOR_PIN))  # Usar DHT11. Si usas DHT22, cambia a dht.DHT22()

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

# Función para leer el estado del sensor KY-015
def read_temperature_humidity():
    try:
        sensor.measure()  # Realizar la medición
        temperature = sensor.temperature()  # Obtener la temperatura en grados Celsius
        humidity = sensor.humidity()  # Obtener la humedad en porcentaje
        return temperature, humidity
    except Exception as e:
        print(f"Error al leer el sensor: {e}")
        return None, None

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
        # Leer los datos del sensor
        temperature, humidity = read_temperature_humidity()
        
        if temperature is not None and humidity is not None:
            # Imprimir datos en la consola
            print(f"Temperatura: {temperature}°C, Humedad: {humidity}%")
            
            # Crear un mensaje JSON con los datos del sensor
            mqtt_message = json.dumps({
                "temperature": temperature,
                "humidity": humidity
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudieron leer los datos del sensor.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(2)  # Esperar 2 segundos entre mediciones