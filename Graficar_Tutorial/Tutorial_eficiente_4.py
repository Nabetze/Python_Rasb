# Si funciona, grafica a una buena velocidad sin problemas.
# Tambien tiene un botón para iniciar o parar
# Tiene un bloque para enviar y recibir datos.
# Solamente grafica el angulo y referencia.

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

# Datos iniciales:
gData = []
gData.append([0]) # Eje X
gData.append([0]) # Eje Y

t_m = []    # Vector de target
t_m.append(0)

u_m = []    # Vector de U.
u_m.append(0)

# Configuración del cliente MQTT
MQTT_BROKER = "10.100.239.29" #"192.168.18.42" 
MQTT_TOPIC = "datos/bno055"

#Configuramos la gráfica
fig = plt.figure()
gs = GridSpec(4, 2, figure=fig)

axth = plt.subplot(gs[0, 1])
axu  = plt.subplot(gs[1, 1])


# Variables para almacenar los datos recibidos 
line_th, = axth.plot(gData[0], gData[1])
line_t, = axth.plot(gData[0], t_m)
line_u, = axu.plot(gData[0], u_m)


axth.set_xlabel('Muestras')
axth.set_ylabel('Ángulo (grados)')
axth.set_ylim(-90, 90)  
axth.set_xlim(0, 200)

# Voltaje máximo de entrada (medido en la Raspberry):
Vol_rasp = 5.4  #Vol.

limite = 30.0  #[kPA], máxima presion en el regulador electronico.
u = 0.0        #[kPa], valor inicial de la ley de control.

# Configura las constantes del controlador PID
kp = 0.01
ki = 0.01
kd = 0.0
prev_error = 0.0
integral = 0.0

# Configuraciones necesarias para la referencia trapezoidal:----------------------------------------
tsubida = 3    # t2 - t1
tbajada = 5    # t4 - t3
testatico = 5  # t3 - t2
tinicial = 5   # t1

#Duracion total:
ttotal = tsubida + tbajada + testatico + tinicial

# Obtenemos los puntos de tiempo:
t1 = tinicial
t2 = tsubida + t1
t3 = testatico + t2
t4 = tbajada + t3

# Valores maximos y minimos de angulo:
Amin = 10 #[grados]
Amax = 60 #[grados]

# Variable de referencia:
target = 0

# Contador de ciclos:
Num_ciclos = -1

# Limite de cilcos:
Lim_ciclos = 0

# Angulo
angulo = 0

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    if stop:    # Vemos si es que está prendido el sistema, si no no almacenamos.
        mensaje_decodificado = message.payload.decode("utf-8")

        global angulo

        angulo = float(mensaje_decodificado)
        # gData[1].append(angulo)

        # if len(gData[1]) > 200:

        #     gData[1].pop(0)


# Función que actualizará los datos de la gráfica
# Se llama periódicamente desde el 'FuncAnimation'
def update_line(frame, lineth, lineu, linet):

    global stop, u, error, prev_error, integral, derivativo, target
    global t1, t2, t3, t4, t_inicial, t_anterior, tsubida, tbajada, ttotal
    global Amin, Amax, Num_ciclos
    global angulo
    global gData, u_m, t_m

    # Paramos el sistema si es que el número de ciclos llegó al límite o si es que se puso stop:
    if Num_ciclos == -1 or not(stop):

        # Graficamos lo que tenemos
        lineth.set_data(range(len(gData[1])), gData[1])
        linet.set_data(range(len(gData[1])), t_m)
        lineu.set_data(range(len(gData[1])), u_m)
    
        # Volvemos la referencia 0.
        target = 0

        # Apagamos el regulador electrónico
        u = 0

        # Lee la orientación del BNO055
        orientacion = angulo

        # Volvemos 0 tanto al error como la derivada del error:
        error_medido = 0
        derror_medido = 0
 
        # Restauramos los valores iniciales:
        t1 = tinicial
        t2 = tsubida + t1
        t3 = testatico + t2
        t4 = tbajada + t3

        # Almacenamos los datos
        gData[1].append(angulo)
        gData[0].append(frame)
        u_m.append(target)


        if len(gData[1]) > 200:

            gData[1].pop(0)
            u_m.pop(0)

        # Actualizamos el t_inicial y reseteamos los otros tiempos: 
        t_inicial = time.time()
        t_anterior = time.time() - t_inicial

    elif stop:
        lineth.set_data(range(len(gData[1])), gData[1])
        linet.set_data(range(len(gData[1])), t_m)
        lineu.set_data(range(len(gData[1])), u_m)

    
        t = time.time() - t_inicial #[s]

        if t <= t1:
                
            target = Amin
                
        elif t <= t2:
                
            a = (Amax - Amin)/(tsubida)
                
            target = a*(t - t2) + Amax
                
        elif t <= t3:
                
            target = Amax
                
        elif t <= t4:
                
            c = (Amin - Amax)/(tbajada)
                
            target = c*(t - t3) + Amax
                
        else:
                
            target = Amin
                
            # Actualizamos los límites:
            t1 = t1 + ttotal
            t2 = t2 + ttotal
            t3 = t3 + ttotal
            t4 = t4 + ttotal
                
            # Sumamos un ciclo:
            Num_ciclos = Num_ciclos + 1

            # Si llegamos al último ciclo entonces "apagamos todo":
            if Num_ciclos == Lim_ciclos:
                Num_ciclos = -1
                

        # Lee la orientación del BNO055
        orientacion = angulo

        # Convierte la orientación a un valor de error para el controlador PID
        error = target - orientacion

        # Calcula los términos proporcional, integral y derivativo del controlador PID
        proporcional = kp * error
        integral += ki * error
        derivativo = kd * (error - prev_error) / 0.05
        prev_error = error

        # Calcula el valor de salida del controlador PID [kPa]
        u = proporcional + integral + derivativo

        # Limita la salida a los límites del regulador electrónico (0-[limite])
        u = min(max(u, 0), limite)

        # Convierte el voltaje a un valor de 12 bits para el MCP4725
        valor = int(5 * 65535 / Vol_rasp * u / limite)

        # Almacenamos los datos
        gData[1].append(angulo)
        gData[0].append(frame)
        t_m.append(target)
        u_m.append(u)


        if len(gData[1]) > 200:

            gData[1].pop(0)
            t_m.pop(0)
            u_m.pop(0)


    
    return lineth, lineu, linet

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
def Lim_Ciclos_submit(text):
    # Convertir el valor ingresado a un número de punto flotante
    global Lim_ciclos, Num_ciclos

    # Guardamos lo que recibimos
    Lim_ciclos = float(text)

    # Colocamos 0 para que inicie el bucle
    Num_ciclos = 0

    # Hacer algo con el valor ingresado, por ejemplo imprimirlo en la consola
    print(f"Valor ingresado: {Lim_ciclos}")

# Crear un cuadro de texto en la posición (0.1, 0.9) de la figura
cuadro_texto_Lim_Ciclos = TextBox(fig.add_subplot(gs[1, 0]), "Ingresar Num Ciclos", initial="0")

# Asociar la función on_submit al evento "submit" del cuadro de texto
cuadro_texto_Lim_Ciclos.on_submit(Lim_Ciclos_submit)


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

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()

# Tiempo inicial:
t_inicial = time.time()
t_anterior = time.time() - t_inicial

# Configuramos la función que "animará" nuestra gráfica
line_ani = animation.FuncAnimation(fig, update_line, fargs=(line_th, line_u, line_t),
interval=50, blit=True)

# ---------------

plt.show()
