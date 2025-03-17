from machine import Pin, PWM
from time import sleep
import network
from umqtt.simple import MQTTClient

led = PWM(Pin(14), freq=500)  

VERDE = 550    
AZUL = 150    
MQTT_Broker = "192.168.226.169"
MQTT_TOPIC = "utng/ky034"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "KY034_RGBLED"

def wifi_connect():
    print("Conectando", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect("S20 Ultra", "123456789")
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi conectada")

def llegada_mensaje(topic, msg):
    print("Mensaje recibido:", msg)
    if msg == b'1':
        ledPin.value(1)  
    elif msg == b'0':
        ledPin.value(0)

def subscribir():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_Broker, port=MQTT_PORT, keepalive=0)
    client.set_callback(llegada_mensaje)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print("Conectado a %s, suscrito a %s" % (MQTT_Broker, MQTT_TOPIC))
    return client

wifi_connect()
client = subscribir()

while True:
    client.check_msg()
    
    led.duty(VERDE)
    client.publish(MQTT_TOPIC,"Verde")
    sleep(1)
    led.duty(AZUL)
    client.publish(MQTT_TOPIC,"Azul")
    sleep(1)