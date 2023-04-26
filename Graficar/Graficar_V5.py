import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk

# Datos iniciales:
gData = []
gData.append([0]) # Eje X
gData.append([0]) # Eje Y


# Configuración del cliente MQTT
MQTT_BROKER = "10.100.236.192"
MQTT_TOPIC = "datos/bno055"

#Configuramos la gráfica
fig = plt.figure()
ax = fig.add_subplot(111)

# Variables para almacenar los datos recibidos 
hl, = plt.plot(gData[0], gData[1])

ax.set_xlabel('Muestras')
ax.set_ylabel('Ángulo (grados)')
ax.set_ylim(-90, 90)  
ax.set_xlim(0, 200)

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    mensaje_decodificado = message.payload.decode("utf-8")
    global angulo
    angulo = float(mensaje_decodificado)
    gData[1].append(angulo)
    if len(gData[1]) > 200:
        gData[1].pop(0)

# Función que actualizará los datos de la gráfica
# Se llama periódicamente desde el 'FuncAnimation'
def update_line(num, hl, data):
    hl.set_data(range(len(data[1])), data[1])
    return hl,

# Función para iniciar la animación
def start_animation():
    mqttClient.loop_start()
    line_ani.event_source.start()

# Función para detener la animación
def stop_animation():
    mqttClient.loop_stop()
    line_ani.event_source.stop()

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)


# Configuramos la función que "animará" nuestra gráfica
line_ani = animation.FuncAnimation(fig, update_line, fargs=(hl, gData),
interval=50, blit=False)


# Creamos la GUI
root = tk.Tk()
root.title("Control de animación")

# Creamos los botones de inicio y detención
start_button = tk.Button(root, text="Iniciar", command=start_animation)
stop_button = tk.Button(root, text="Detener", command=stop_animation)

# Ubicamos los botones en la ventana
start_button.pack(side=tk.LEFT)
stop_button.pack(side=tk.LEFT)

# Mostramos la ventana
root.mainloop()
