import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np
import paho.mqtt.client as mqtt

# Configuración del cliente MQTT
MQTT_BROKER = "10.100.232.87"
MQTT_TOPIC = "datos/bno055"

# Datos iniciales:
gData = []
gData.append([0]) # Eje X
gData.append([0]) # Eje Y

fig = plt.Figure()
ax = fig.add_subplot(111)

root = tk.Tk()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    mensaje_decodificado = message.payload.decode("utf-8")
    global angulo
    angulo = float(mensaje_decodificado)

    gData[1].append(angulo)

    if len(gData[1]) > 200:
        gData[1].pop(0)

    ax.clear()
    ax.plot(gData[1])

    # Actualiza el widget del gráfico
    canvas.draw()


# Crea un cliente MQTT y se suscribe al tópico correspondiente
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()

# Inicia la aplicación de Tkinter
root.mainloop()

# Detiene el bucle del cliente MQTT cuando se cierra la aplicación
mqttClient.loop_stop()
mqttClient.disconnect()
