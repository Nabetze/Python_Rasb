import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np

# Configuración del cliente MQTT
MQTT_BROKER = "10.100.232.87"
MQTT_TOPIC = "datos/bno055"

# Variables para almacenar los datos recibidos
fig, ax = plt.subplots()    
ax.set_xlabel('Muestras')
ax.set_ylabel('Ángulo (grados)')
ax.set_ylim(-90, 90)  

xdata = []
ydata = []



# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    mensaje_decodificado = message.payload.decode("utf-8")
    global angulo
    angulo = float(mensaje_decodificado)
    xdata.append(len(xdata))
    ydata.append(angulo)
    if len(xdata) > 50:
        xdata.pop(0)
        ydata.pop(0)
    ax.set_xlim(max(0, len(xdata)-50), len(xdata))  

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()


while True:
    ax.plot(xdata,ydata, 'r', label='Angulo')
    plt.pause(0.05)
    #ax.clear()
    print(angulo)
