import network
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import time
import json

# Configuración WiFi
WIFI_SSID = "S20 Ultra"
WIFI_PASSWORD = "123456789"

# Configuración MQTT
MQTT_BROKER = "192.168.202.169"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "KY035_HallSensor"
MQTT_TOPIC_PUBLISH = "sensor/hall"  # Tema para publicar datos del sensor
MQTT_PORT = 1883

# Configuración del KY-035 (Sensor de Efecto Hall Analógico)
SENSOR_PIN = 34  # GPIO conectado al pin de señal del KY-035 (debe ser un pin ADC)
sensor = ADC(Pin(SENSOR_PIN))  # Configurar el pin como entrada analógica
sensor.atten(ADC.ATTN_11DB)  # Configurar la atenuación para un rango de 0-3.3V

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

# Función para leer el estado del sensor KY-035
def read_hall_sensor():
    try:
        adc_value = sensor.read()  # Leer el valor analógico del sensor (0-4095)
        voltage = adc_value * (3.3 / 4095)  # Convertir a voltaje (0-3.3V)
        return adc_value, voltage
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
        adc_value, voltage = read_hall_sensor()
        
        if adc_value is not None and voltage is not None:
            # Imprimir datos en la consola
            print(f"Valor ADC: {adc_value}, Voltaje: {voltage:.2f}V")
            
            # Crear un mensaje JSON con los datos del sensor
            mqtt_message = json.dumps({
                "adc_value": adc_value,
                "voltage": round(voltage, 2)
            })
            
            # Publicar el mensaje JSON en el broker MQTT
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudieron leer los datos del sensor.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(0.5)  # Esperar 0.5 segundos entre mediciones