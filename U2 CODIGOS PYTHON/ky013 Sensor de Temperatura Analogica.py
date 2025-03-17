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
MQTT_CLIENT_ID = "KY013_TempSensor"
MQTT_TOPIC_PUBLISH = "utng/tempAna"  # Tema para publicar datos del sensor
MQTT_PORT = 1883

# Configuración del KY-013 (Sensor de Temperatura Analógico)
SENSOR_PIN = 34  # GPIO conectado al pin de señal del KY-013 (debe ser un pin ADC)
adc = ADC(Pin(SENSOR_PIN))  # Configurar el pin como entrada analógica
adc.atten(ADC.ATTN_11DB)  # Configurar la atenuación para un rango de 0-3.3V

# Constantes para cálculo de temperatura
BETA = 3950  # Valor beta del termistor 
R0 = 10000   # Resistencia nominal del termistor a 25°C
T0 = 298.15  # Temperatura nominal en Kelvin (25°C)

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

# Función para leer la temperatura del sensor KY-013
def read_temperature():
    try:
        # Leer el valor analógico del sensor
        adc_value = adc.read()  # Valor entre 0 y 4095
        
        # Validar que el valor no sea extremo (0 o 4095)
        if adc_value == 0 or adc_value == 4095:
            print("Valor ADC fuera de rango:", adc_value)
            return None
        
        # Convertir a voltaje (0-3.3V)
        voltage = adc_value / 4095 * 3.3
        print(f"Voltaje leído: {voltage:.3f}V")
        
        # Calcular la resistencia del termistor
        R = (3.3 - voltage) / max(voltage, 0.001) * R0  # Evitar división por cero
        print(f"Resistencia del termistor: {R:.2f} ohms")
        
        # Calcular la temperatura en Kelvin usando la ecuación de Steinhart-Hart simplificada
        T_kelvin = 1 / ((1 / T0) + (1 / BETA) * (3.3 / max(voltage, 0.001) - 1))
        
        # Convertir a grados Celsius
        temperature = T_kelvin - 273.15
        return temperature
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
    machine.reset()

# Bucle principal
while True:
    try:
        # Leer la temperatura del sensor
        temperature = read_temperature()
        
        if temperature is not None:
            # Imprimir datos en la consola
            print(f"Temperatura: {temperature:.2f}°C")
            
            # Crear un mensaje JSON con los datos del sensor
            mqtt_message = json.dumps({
                "temperature": temperature
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudo leer la temperatura del sensor.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
   
    time.sleep(3)  