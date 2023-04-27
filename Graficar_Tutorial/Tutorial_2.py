import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot as plt


import tkinter as tk
from tkinter import ttk

# Librerias del MQTT:
import paho.mqtt.client as mqtt
import numpy as np

# Configuración del cliente MQTT
MQTT_BROKER = "10.100.236.192"
MQTT_TOPIC = "datos/bno055"

# Datos iniciales:
gData = []
gData.append([0]) # Eje X
gData.append([0]) # Eje Y

LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(10,6), dpi=100)
a = f.add_subplot(111)

hl, = plt.plot(gData[0], gData[1])

class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Sea of BTC client")
        
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, BTCe_Page):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text=("""ALPHA Bitcoin trading application
        use at your own risk. There is no promise
        of warranty."""), font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Agree",
                            command=lambda: controller.show_frame(BTCe_Page))
        button1.pack()

        button2 = ttk.Button(self, text="Disagree",
                            command=quit)
        button2.pack()



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()




class BTCe_Page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()


        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    mensaje_decodificado = message.payload.decode("utf-8")
    angulo = float(mensaje_decodificado)
    gData[1].append(angulo)

    if len(gData[1]) > 200:
        gData[1].pop(0)

def animate(num, h, data):

    h.set_data(range(len(data[1])), data[1])
    
    a.plot(data[1])
    a.clear()

    return h,

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()

app = SeaofBTCapp()
#ani = animation.FuncAnimation(f, animate, interval=50)
ani = animation.FuncAnimation(f, animate, fargs=(hl, gData),
interval=50, blit=False)
app.mainloop()
