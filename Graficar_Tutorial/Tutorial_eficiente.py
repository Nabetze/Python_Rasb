# Si funciona,  grafica sin problemas pero solo e suna grafica, no es interactivo.

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np

# Datos iniciales:
gData = []
gData.append([0]) # Eje X
gData.append([0]) # Eje Y
muestra = -1      # Numero de muestra


# Configuración del cliente MQTT
MQTT_BROKER = "192.168.18.42"#"10.100.236.192"
MQTT_TOPIC = "datos/bno055"

#Configuramos la gráfica
fig = plt.figure()
ax = fig.add_subplot(111)

# Variables para almacenar los datos recibidos 
line, = plt.plot(gData[0], gData[1])

ax.set_xlabel('Muestras')
ax.set_ylabel('Ángulo (grados)')
ax.set_ylim(-90, 90)  
ax.set_xlim(0, 200)

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    mensaje_decodificado = message.payload.decode("utf-8")

    global muestra
    muestra += 1
    gData[0].append(muestra)

    angulo = float(mensaje_decodificado)
    gData[1].append(angulo)

    if len(gData[1]) > 200:

        gData[1].pop(0)
        gData[0].pop(0)


# Función que actualizará los datos de la gráfica
# Se llama periódicamente desde el 'FuncAnimation'
def update_line(frame, line, data):

    line.set_data(data[0], data[1])

    rescale = False

    # Si no llegamos al límite inferior reducimos el límite.
    if data[1][-1] < ax.get_ylim()[0]:
        ax.set_ylim(data[1][-1] - 0.1, ax.get_ylim()[1])

    # Si superamos el limite superior crecemos la gráfica 0.1.
    if data[1][-1] > ax.get_ylim()[1]:
        ax.set_ylim(ax.get_ylim()[0], data[1][-1] + 0.1)

    #
    if data[0][-1] > ax.get_xlim()[1]:
        ax.set_ylim(ax.get_xlim()[0] + 200, ax.get_xlim()[1] + 200)

    if data[1][-1] < ax.get_ylim()[0]:
        ax.set_ylim(data[1][-1] - 0.1, ax.get_ylim()[1])

    return line,


# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()


# Configuramos la función que "animará" nuestra gráfica
line_ani = animation.FuncAnimation(fig, update_line, fargs=(line, gData),
interval=50, blit=True)

# ---------------

plt.show()
