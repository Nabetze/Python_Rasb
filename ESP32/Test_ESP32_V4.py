#Test con MQTT

import paho.mqtt.client as mqtt

MQTT_SERVER = "10.100.232.87" # Cambiar por la dirección IP de la Raspberry Pi
MQTT_PORT = 1883
MQTT_TOPIC = "datos/bno055"

def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT con código de resultado: " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print("Mensaje recibido en el tema " + msg.topic + ": " + str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, MQTT_PORT, 60)

client.loop_forever()
