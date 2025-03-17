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
MQTT_CLIENT_ID = "KY023_Joystick"
MQTT_TOPIC_PUBLISH = "utng/ky023"  # Tema para publicar los datos del joystick
MQTT_PORT = 1883

# Configuración del KY-023 (Joystick)
JOYSTICK_X_PIN = 34  # GPIO conectado al eje X (analógico)
JOYSTICK_Y_PIN = 35  # GPIO conectado al eje Y (analógico)
JOYSTICK_BUTTON_PIN = 14  # GPIO conectado al botón (digital)

adc_x = ADC(Pin(JOYSTICK_X_PIN))
adc_y = ADC(Pin(JOYSTICK_Y_PIN))
button = Pin(JOYSTICK_BUTTON_PIN, Pin.IN, Pin.PULL_UP)

adc_x.atten(ADC.ATTN_11DB)
adc_y.atten(ADC.ATTN_11DB)

# Umbral para detectar direcciones (ajustar según calibración)
CENTER_THRESHOLD = 2048  # Valor central del joystick (aproximadamente la mitad de 0-4095)
DEAD_ZONE = 500  # Margen para evitar ruido cerca del centro

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

# Función para leer los valores del joystick
def read_joystick():
    try:
        # Leer valores de los ejes X e Y (0-4095)
        x_value = adc_x.read()
        y_value = adc_y.read()
        
        # Leer el estado del botón (0 = presionado, 1 = no presionado)
        button_state = button.value()
        
        return x_value, y_value, button_state
    except Exception as e:
        print(f"Error al leer el joystick: {e}")
        return None, None, None

# Función para determinar la dirección del joystick
def get_direction(x_value, y_value):
    if abs(x_value - CENTER_THRESHOLD) < DEAD_ZONE and abs(y_value - CENTER_THRESHOLD) < DEAD_ZONE:
        return "centro"
    elif x_value < CENTER_THRESHOLD - DEAD_ZONE:
        return "izquierda"
    elif x_value > CENTER_THRESHOLD + DEAD_ZONE:
        return "derecha"
    elif y_value < CENTER_THRESHOLD - DEAD_ZONE:
        return "arriba"
    elif y_value > CENTER_THRESHOLD + DEAD_ZONE:
        return "abajo"
    else:
        return "centro"

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
        # Leer los valores del joystick
        x_value, y_value, button_state = read_joystick()
        
        if x_value is not None and y_value is not None and button_state is not None:
            # Determinar la dirección del joystick
            direction = get_direction(x_value, y_value)
            
            # Imprimir datos en la consola
            print(f"Dirección: {direction}, Botón: {'Presionado' if button_state == 0 else 'No Presionado'}")
            
            # Crear un mensaje JSON con los datos del joystick
            mqtt_message = json.dumps({
                "sensor": "ky023",
                "valor": direction,
                "boton": "presionado" if button_state == 0 else "libre"
            })
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
        else:
            print("No se pudieron leer los datos del joystick.")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(1)  # Esperar 100 ms entre mediciones