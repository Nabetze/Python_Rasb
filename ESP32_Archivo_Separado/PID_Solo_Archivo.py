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
import os

# Crear una tubería
pipe_read, pipe_write = os.pipe()

# Datos iniciales:

# Configuración del cliente MQTT
# Utec_Alumno: "10.100.239.161"
# Casa: "192.168.18.42"
# Datos: "192.168.43.101"

MQTT_BROKER = "10.100.239.161"
MQTT_TOPIC_Theta1 = "datos/bno055"
MQTT_TOPIC_Servo = "datos/servo"
MQTT_TOPIC_U = "datos/u"

stop = False
actual_angle = 0
change = False

# Sermotor's angle of rotation:
beta = 0

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    if stop:    # Vemos si es que está prendido el sistema, si no no almacenamos.
        mensaje_decodificado = message.payload.decode("utf-8")

        global actual_angle

        actual_angle = float(mensaje_decodificado)

# ----------------------

# --------------------------------- Main:
PID_1 = PID("Pierna_Izquierda")

reference = Trapezoidal_Reference("Referencia")

# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC_Theta1)
mqttClient.loop_start()


# We go to the inicial position of the Servo motor:
reference.Activade_servo(0, MQTT_TOPIC_Servo , mqttClient)

# Tiempo inicial:
t_inicial = time.time()
t_anterior = time.time() - t_inicial

# Función que actualizará los datos de la gráfica
# Se llama periódicamente desde el 'FuncAnimation'
while(1):

    # Paramos el sistema si es que el número de ciclos llegó al límite o si es que se puso stop:
    if reference.Num_ciclos == -1 or not(stop):

        # Clearing the variables:
        PID_1.Stop_Controll()

        # Lee la orientación del BNO055
        orientacion = actual_angle

        # We don't have target:
        target = 0

        # Restauramos los valores iniciales:
        reference.Restart_points_of_time()

        # Enviamos los datos a otro archivo.
        os.write(pipe_write, f"{orientacion},{target},{PID_1.u}\n".encode())

        # Sending the pressuare value to the DAC.
        PID_1.Send_u (PID_1.u, MQTT_TOPIC_U, mqttClient)

        # Actualizamos el t_inicial y reseteamos los otros tiempos: 
        t_inicial = time.time()
        t_anterior = time.time() - t_inicial


    elif stop:

        t = time.time() - t_inicial #[s]

        target, change = reference.Compute_target(t)

        # Lee la orientación del BNO055
        orientacion = actual_angle
                
        # We compute the pressuare value using PID.
        PID_1.Calculate_u (orientacion, target)

        # Sending the pressuare value to the DAC.
        PID_1.Send_u (PID_1.u, MQTT_TOPIC_U, mqttClient)

        # Enviamos los datos a otro archivo.
        os.write(pipe_write, f"{orientacion},{target},{PID_1.u}\n".encode())

        # If we are in an even cicle it means that we need to change of legh:
        if change:

            #If beta = 0 means that we are in the first leg:
            if beta == 0:

                # Change the value:
                beta = 180

            # Otherwise, we are in te second leg:
            else:
                beta = 0

            # Move servo Beta angle:
            reference.Activade_servo(beta, MQTT_TOPIC_Servo , mqttClient)

            change = False



