import network
from umqtt.simple import MQTTClient
from machine import Pin
import time
import json

# Configuración WiFi
SSID_WIFI = "S20 Ultra"
CONTRASENA_WIFI = "123456789"

# Configuración MQTT
BROKER_MQTT = "192.168.226.169"  # Usa un broker público o local
USUARIO_MQTT = ""
CONTRASENA_MQTT = ""
ID_CLIENTE_MQTT = "KY040_Encoder"
TEMA_MQTT_PUBLICAR = "utng/ky040"  # Tema para publicar estados del encoder
PUERTO_MQTT = 1883

# Configuración de pines
PIN_ENCODER_CLK = 14  # GPIO conectado al pin CLK del encoder
PIN_ENCODER_DT = 12   # GPIO conectado al pin DT del encoder
PIN_BOTON_SW = 13     # GPIO conectado al pin SW del encoder

# Configurar pines del encoder
pin_clk = Pin(PIN_ENCODER_CLK, Pin.IN, Pin.PULL_UP)
pin_dt = Pin(PIN_ENCODER_DT, Pin.IN, Pin.PULL_UP)
pin_sw = Pin(PIN_BOTON_SW, Pin.IN, Pin.PULL_UP)

# Variables para el encoder
estado_anterior = pin_clk.value()
contador = 0
boton_presionado = False

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID_WIFI, CONTRASENA_WIFI)
    while not wifi.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi conectada!")
    print("Dirección IP:", wifi.ifconfig()[0])

# Función para conectar al broker MQTT
def conectar_broker_mqtt():
    try:
        cliente = MQTTClient(ID_CLIENTE_MQTT, BROKER_MQTT, port=PUERTO_MQTT, user=USUARIO_MQTT, password=CONTRASENA_MQTT)
        cliente.connect()
        print(f"Conectado al broker MQTT: {BROKER_MQTT}, Tema: {TEMA_MQTT_PUBLICAR}")
        return cliente
    except Exception as e:
        print(f"Error al conectar al broker MQTT: {e}")
        raise

# Conectar a WiFi y MQTT
try:
    conectar_wifi()
    cliente_mqtt = conectar_broker_mqtt()
    time.sleep(1)
except Exception as e:
    print(f"Error al conectar: {e}")
    time.sleep(5)
    from machine import reset
    reset()

# Bucle principal
while True:
    try:
        # Detectar giros del encoder
        estado_actual = pin_clk.value()
        if estado_actual != estado_anterior:
            if pin_dt.value() != estado_actual:
                contador += 1
                direccion = "Horario"
            else:
                contador -= 1
                direccion = "Antihorario"
            
            # Publicar el estado del encoder en MQTT
            mensaje_mqtt = json.dumps({
                "contador": contador,
                "direccion": direccion
            })
            cliente_mqtt.publish(TEMA_MQTT_PUBLICAR, mensaje_mqtt)
            print(f"Contador: {contador}, Dirección: {direccion}")
        
        estado_anterior = estado_actual
        
        # Detectar pulsaciones del botón
        if pin_sw.value() == 0:  # Botón presionado
            if not boton_presionado:
                boton_presionado = True
                print("Botón presionado")
                
                # Publicar evento de botón presionado en MQTT
                mensaje_mqtt = json.dumps({
                    "boton": "PRESIONADO",
                    "contador": contador
                })
                cliente_mqtt.publish(TEMA_MQTT_PUBLICAR, mensaje_mqtt)
        else:
            boton_presionado = False
        
        time.sleep(0.1)  # Pequeño delay para evitar lecturas demasiado rápidas
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        time.sleep(5)
        from machine import reset
        reset()