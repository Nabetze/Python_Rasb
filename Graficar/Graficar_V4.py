import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
from tkinter import Tk, Frame,Button,Label, ttk
import numpy as np

# Datos iniciales:
gData = []
gData.append([0]) # Eje X
gData.append([0]) # Eje Y


# Configuración del cliente MQTT
MQTT_BROKER = "10.100.232.87"
MQTT_TOPIC = "datos/bno055"

#Configuramos la gráfica
fig = plt.figure()
ax = fig.add_subplot(111)

# Variables para almacenar los datos recibidos 
hl, = plt.plot(gData[0], gData[1])

plt.title("Grafica de angulo tiempo real",color='white',size=16, family="Arial")
ax.set_xlabel('Muestras')
ax.set_ylabel('Ángulo (grados)')
ax.set_ylim(-90, 90)  
ax.set_xlim(0, 200)


# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    mensaje_decodificado = message.payload.decode("utf-8")
    global angulo
    angulo = float(mensaje_decodificado)
    #xdata.append(len(xdata))
    gData[1].append(angulo)
    if len(gData[1]) > 200:
        #xdata.pop(0)
        gData[1].pop(0)
        #ax.clear()
    #ax.set_xlim(max(0, len(xdata)-50), len(xdata))  

# Función que actualizará los datos de la gráfica
# Se llama periódicamente desde el 'FuncAnimation'
def update_line(num, hl, data):
    hl.set_data(range(len(data[1])), data[1])
    return hl,


# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()


# Configuramos la función que "animará" nuestra gráfica


plt.show()

def iniciar():	
	global line_ani
	line_ani = animation.FuncAnimation(fig, update_line, fargs=(hl, gData),
                                        interval=50, blit=False) 
	canvas.draw()

def pausar():
	line_ani.event_source.stop() 

def reanudar():
	line_ani.event_source.start()

# De la grafica:
ventana = Tk()
ventana.geometry('642x535')
ventana.wm_title('Grafica Matplotlib Animacion')
ventana.minsize(width=642,height=535)

frame = Frame(ventana,  bg='gray22',bd=3)
frame.pack(expand=1, fill='both')

canvas = FigureCanvasTkAgg(fig, master = frame)  
canvas.get_tk_widget().pack(padx=5, pady=5 , expand=1, fill='both') 


Button(frame, text='Grafica Datos', width = 15, bg='purple4',fg='white', command=iniciar).pack(pady =5,side='left',expand=1)
Button(frame, text='Pausar', width = 15, bg='salmon',fg='white', command=pausar).pack(pady =5,side='left',expand=1)
Button(frame, text='Reanudar', width = 15, bg='green',fg='white', command=reanudar).pack(pady =5,side='left',expand=1)

ventana.mainloop()