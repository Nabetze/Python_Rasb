import paho.mqtt.client as mqtt
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation



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
    if len(xdata) > 50:
        xdata.pop(0)
        ydata.pop(0)
    line.set_data(xdata, ydata)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()

# Función para encender/apagar el sistema
def toggle_system():
    global system_on
    system_on = not system_on
    if system_on:
        mqttClient.loop_start()
    else:
        mqttClient.loop_stop()

# Configuración de la GUI
fig, ax = plt.subplots()
line, = ax.plot(xdata, ydata, 'r', label='Angulo')
ax.set_xlabel('Muestras')
ax.set_ylabel('Ángulo (grados)')
ax.set_ylim(-90, 90)
ax.set_xlim(0, 50)
ax.legend()

system_on = True

root = tk.Tk()
root.geometry("500x300")


canvas = FigureCanvasTkAgg(fig, master = frame)  
canvas.get_tk_widget().pack(padx=5, pady=5 , expand=1, fill='both') 

button = tk.Button(root, text="Encender/Apagar", command=toggle_system)
button.pack(side="bottom")

root.mainloop()
