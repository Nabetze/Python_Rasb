import tkinter as tk
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import matplotlib.animation as animation

# Configuración del cliente MQTT
MQTT_SERVER = "10.100.236.192"
MQTT_PORT = 1883
MQTT_TOPIC = "datos/bno055"

# Configuración de la ventana de GUI
root = tk.Tk()
root.title("Gráfica de datos MQTT")

# Configuración de la gráfica
fig = plt.Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(1, 1, 1)
line, = ax.plot([], [])
data = deque(maxlen=100)  # Almacenará hasta los últimos 100 valores

# Función que se llama cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    # Agrega el valor del ángulo a la lista de datos
    data.append(float(message.payload.decode()))

# Función que se llama para actualizar la gráfica
def update_graph(frame):
    # Actualiza los datos de la gráfica con los datos almacenados
    line.set_data(list(range(len(data))), data)
    ax.relim()
    ax.autoscale_view(True,True,True)
    return line,

# Conexión a MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_SERVER, MQTT_PORT)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.on_message = on_message
mqtt_client.loop_start()

# Crea una animación para actualizar la gráfica cada 100 milisegundos
ani = animation.FuncAnimation(fig, update_graph, interval=100)

# Inicia la ventana de la GUI
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# Función principal de la GUI
def main():
    root.mainloop()

if __name__ == '__main__':
    main()
