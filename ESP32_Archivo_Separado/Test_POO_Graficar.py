# Si funciona, grafica a una buena velocidad sin problemas.
# Tambien tiene un botón para iniciar o parar
# Tiene un bloque para enviar y recibir datos.
# Solamente grafica el angulo y referencia.
# Puedes ingresar el tiempo de subida, bajada
# Puedes ver la dey de control también
# Envia a la DAC el valor de presion.
# El problema es que realiza el control en el mismo codigo.

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import threading
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
import time
from PID_VPAM import PID
from Trapezoidal_Reference import Trapezoidal_Reference

# Datos iniciales:

# Angle's vector
angle_m = []
angle_m.append(0)

# Sample's vector
sample_m = []
sample_m.append(0)

# Target's vector
t_m = []    
t_m.append(0)

# Pressure's vector
u_m = []    
u_m.append(0)

# Configuración del cliente MQTT
MQTT_BROKER = "10.100.239.29" #"192.168.18.42" 
MQTT_TOPIC = "datos/bno055"

#Configuramos la gráfica
fig = plt.figure(figsize=(5.11, 2.75))
gs = GridSpec(4, 2, figure=fig, width_ratios=[1, 4])

axth = plt.subplot(gs[0:2, 1])
axth.grid(True)
axu  = plt.subplot(gs[2:4, 1])
axu.grid(True)


# Variables para almacenar los datos recibidos 
line_th, = axth.plot(sample_m, angle_m, linewidth=2)
line_t, = axth.plot(sample_m, t_m, linewidth=2)
line_u, = axu.plot(sample_m, u_m, linewidth=2)


axth.set_xlabel('Muestras')
axth.set_ylabel('Ángulo (grados)')
axth.set_ylim(-5, 90)  
axth.set_xlim(0, 400)

axu.set_xlabel('Muestras')
axu.set_ylabel('Presion (kPa)')
axu.set_ylim(-5, 20)  
axu.set_xlim(0, 400)


actual_angle = 0

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    if stop:    # Vemos si es que está prendido el sistema, si no no almacenamos.
        mensaje_decodificado = message.payload.decode("utf-8")

        global actual_angle

        actual_angle = float(mensaje_decodificado)

# ----------------------

# Función que actualizará los datos de la gráfica
# Se llama periódicamente desde el 'FuncAnimation'
def update_line(frame, lineth, lineu, linet):

    # Paramos el sistema si es que el número de ciclos llegó al límite o si es que se puso stop:
    if reference.Num_ciclos == -1 or not(stop):

        # Graficamos lo que tenemos
        lineth.set_data(range(len(angle_m)), angle_m)
        linet.set_data(range(len(angle_m)), t_m)
        lineu.set_data(range(len(angle_m)), u_m)
    
        # Clearing the variables:
        PID_1.Stop_Controll()

        # Lee la orientación del BNO055
        orientacion = actual_angle

        # Restauramos los valores iniciales:
        reference.Restart_points_of_time()

        # Almacenamos los datos
        angle_m.append(orientacion)
        sample_m.append(frame)
        t_m.append(target)
        u_m.append(PID_1.u)

        # Sending the pressuare value to the DAC.
        PID_1.Send_u (PID_1.u, "datos/u", mqttClient)

        if len(angle_m) > 400:

            angle_m.pop(0)
            t_m.pop(0)
            u_m.pop(0)

        # Actualizamos el t_inicial y reseteamos los otros tiempos: 
        t_inicial = time.time()
        t_anterior = time.time() - t_inicial


    elif stop:

        # Graficamos lo que tenemos
        lineth.set_data(range(len(angle_m)), angle_m)
        linet.set_data(range(len(angle_m)), t_m)
        lineu.set_data(range(len(angle_m)), u_m)
    
        t = time.time() - t_inicial #[s]

        target = reference.Compute_target(t)
                
        # We compute the pressuare value using PID.
        PID_1.Calculate_u (actual_angle, target)

        # Sending the pressuare value to the DAC.
        PID_1.Send_u (PID_1.u, "datos/u", mqttClient)

        # Almacenamos los datos
        angle_m.append(orientacion)
        sample_m.append(frame)
        t_m.append(target)
        u_m.append(PID_1.u)


        if len(angle_m) > 400:

            angle_m.pop(0)
            t_m.pop(0)
            u_m.pop(0)

    
    return lineth, lineu, linet

# Main:
PID_1 = PID("Pierna_Izquierda")
reference = Trapezoidal_Reference("Referencia")

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()


# Creamos un botón para detener o iniciar la animación
stop = False
def toggle_animation(event):

    global stop
    stop = not stop

# Agregamos un botón para iniciar o apagar:
button_ax = fig.add_subplot(gs[0, 0])
toggle_button = Button(button_ax, 'Start/Stop')
toggle_button.on_clicked(toggle_animation)

# Función que se llama cuando se presiona la tecla "Enter" en el cuadro de texto
def Lim_Ciclos_submit(text, reference):

    # Guardamos lo que recibimos
    reference.Lim_ciclos = float(text)

    # Colocamos 0 para que inicie el bucle
    reference.Num_ciclos = 0

    # Hacer algo con el valor ingresado, por ejemplo imprimirlo en la consola
    print(f"Valor ingresado: {reference.Lim_ciclos}")

# Crear un cuadro de texto en la posición (0.1, 0.9) de la figura
cuadro_texto_Lim_Ciclos = TextBox(fig.add_subplot(gs[1, 0]), "Num Ciclos", initial="0")

# Asociar la función on_submit al evento "submit" del cuadro de texto
cuadro_texto_Lim_Ciclos.on_submit(Lim_Ciclos_submit, reference)


# Función que se llama cuando se presiona la tecla "Enter" en el cuadro de texto
def Ts_submit(text):
    # Convertir el valor ingresado a un número de punto flotante
    global tsubida

    # Guardamos lo que recibimos
    tsubida = float(text)

    # Hacer algo con el valor ingresado, por ejemplo imprimirlo en la consola
    print(f"Valor ingresado: {tsubida}")

# Crear un cuadro de texto en la posición (0.1, 0.9) de la figura
cuadro_texto_tsubida = TextBox(fig.add_subplot(gs[2, 0]), "Ingresar Ts", initial="0")

# Asociar la función on_submit al evento "submit" del cuadro de texto
cuadro_texto_tsubida.on_submit(Ts_submit)

# Función que se llama cuando se presiona la tecla "Enter" en el cuadro de texto
def Tb_submit(text):
    # Convertir el valor ingresado a un número de punto flotante
    global tbajada

    # Guardamos lo que recibimos
    tbajada = float(text)

    # Hacer algo con el valor ingresado, por ejemplo imprimirlo en la consola
    print(f"Valor ingresado: {tbajada}")

# Crear un cuadro de texto en la posición (0.1, 0.9) de la figura
cuadro_texto_tbajada = TextBox(fig.add_subplot(gs[3, 0]), "Ingresar Tb", initial="0")

# Asociar la función on_submit al evento "submit" del cuadro de texto
cuadro_texto_tbajada.on_submit(Tb_submit)


# Tiempo inicial:
t_inicial = time.time()
t_anterior = time.time() - t_inicial

# Configuramos la función que "animará" nuestra gráfica
line_ani = animation.FuncAnimation(fig, update_line, fargs=(line_th, line_u, line_t),
interval=50, blit=True)

# ---------------

plt.show()
