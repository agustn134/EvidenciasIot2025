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
MQTT_CLIENT_ID = "KY031_ImpactSensor"
MQTT_TOPIC_PUBLISH = "utng/ky031"  # Tema para publicar los datos del sensor de impacto
MQTT_PORT = 1883

# Configuración del KY-031 (Sensor de Impacto)
SENSOR_PIN = 14  # GPIO conectado al pin de señal del KY-031
sensor = Pin(SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Configurar como entrada digital con pull-up

# Configuración del LED indicador
LED_PIN = 15  # GPIO conectado al LED
led = Pin(LED_PIN, Pin.OUT)  # Configurar el pin como salida

# Variables para el seguimiento de impactos
last_impact_time = 0
impact_count = 0
impact_detected = False

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

# Función de interrupción para el sensor de impacto
def handle_impact(pin):
    global impact_detected, impact_count, last_impact_time
    current_time = time.time()
    
    # Evitar rebotes - ignorar impactos que ocurren muy rápidamente (menos de 200ms)
    if current_time - last_impact_time > 0.2:
        impact_count += 1
        impact_detected = True
        last_impact_time = current_time
        led.value(1)  # Encender LED cuando se detecta impacto

# Configurar la interrupción para el sensor
sensor.irq(trigger=Pin.IRQ_FALLING, handler=handle_impact)

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
        if impact_detected:
            # Crear un mensaje JSON con la información del impacto
            mqtt_message = json.dumps({
                "event": "impact_detected",
                "count": impact_count,
                "timestamp": time.time()
            })
            
            print(f"¡Impacto detectado! Contador: {impact_count}")
            print(f"Mensaje MQTT enviado: {mqtt_message}")
            
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
            
            # Restablecer la bandera de impacto detectado
            impact_detected = False
            
            # Apagar el LED después de un breve periodo
            time.sleep(0.5)
            led.value(0)
        
        # Publicar actualizaciones periódicas incluso sin impactos
        elif time.time() - last_impact_time > 10:  # Cada 10 segundos sin impactos
            mqtt_message = json.dumps({
                "event": "status_update",
                "count": impact_count,
                "timestamp": time.time()
            })
            
            client.publish(MQTT_TOPIC_PUBLISH, mqtt_message)
            print("Actualización de estado enviada")
    
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        import machine
        machine.reset()
    
    # Pequeña pausa antes de la siguiente iteración
    time.sleep(1)  # Esperar 100 ms entre comprobaciones