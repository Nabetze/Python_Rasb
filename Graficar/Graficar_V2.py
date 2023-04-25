import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np

# Configuración del cliente MQTT
MQTT_BROKER = "10.100.232.87"
MQTT_TOPIC = "datos/bno055"

# Variables para almacenar los datos recibidos
xdata = []
ydata = []

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    mensaje_decodificado = message.payload.decode("utf-8")
    angulo = float(mensaje_decodificado)
    xdata.append(len(xdata))
    ydata.append(angulo)
    if len(xdata) > 100:
        xdata.pop(0)
        ydata.pop(0)
    plt.clf()
    plt.plot(xdata, ydata)
    plt.draw()

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()

# Gráfica en tiempo real
fig = plt.figure()
plt.title('Ángulo del BNO055')
plt.xlabel('Muestras')
plt.ylabel('Ángulo')
plt.ion()
plt.show()

while True:
    plt.pause(0.05)
