# Version que envia los datos de manera correcta para graficar en Node-Red.
# Ademas recibe los valores de Kp, Ki y Kd por node red.
# Se suscribe y publica.
# Se calcula el tiempo de ejecucion.
# Se implemento una referencia trapezoidal.

import time
import board
import busio
import adafruit_bno055
import adafruit_mcp4725
import paho.mqtt.client as mqtt
import json

# Inicializa el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializa el BNO055 en la dirección 0x28
bno = adafruit_bno055.BNO055_I2C(i2c, address=0x28)

# Inicializa el MCP4725 en la dirección 0x60
dac = adafruit_mcp4725.MCP4725(i2c, address=0x60)
# Voltaje máximo de entrada (medido en la Raspberry):
Vol_rasp = 5.4  #Vol.


limite = 30.0  #[kPA], máxima presion en el regulador electronico.
u = 0.0        #[kPa], valor inicial de la ley de control.

# Configura las constantes del controlador PID
kp = 0.2
ki = 0.0
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
Num_ciclos = 0

# Función para actualizar las ganancias del controlador PID
def update_Kp(new_Kp):
    global Kp
    Kp = new_Kp
    print("New gains: Kp={}".format(Kp))

# Función para actualizar las ganancias del controlador PID
def update_Ki(new_Ki):
    global Ki
    Ki = new_Ki
    print("New gains: Ki={}".format(Ki))

# Función para actualizar las ganancias del controlador PID
def update_Kd(new_Kd):
    global Kd
    Kd = new_Kd
    print("New gains: Kd={}".format(Kd))

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    global Kp, Ki, Kd
    print("Message received: topic={}, payload={}".format(message.topic, message.payload))

    # Vemos que tópico es:
    if message.topic == "Kp":
        # Se recibieron nuevas ganancias, se actualizan en el controlador PID
        gain = message.payload.decode("utf-8")
        update_Kp(float(gain))

    elif message.topic == "Ki":
        # Se recibieron nuevas ganancias, se actualizan en el controlador PID
        gain = message.payload.decode("utf-8")
        update_Ki(float(gain))

    elif message.topic == "Kd":
        # Se recibieron nuevas ganancias, se actualizan en el controlador PID
        gain = message.payload.decode("utf-8")
        update_Kd(float(gain))

# Configurar el cliente MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 60)

# Se suscribe al tema "pid/gains"
client.subscribe("Kp")
client.subscribe("Ki")
client.subscribe("Kd")

# Definir el tema MQTT
topic = "Control"


while True:

    t = time.time()

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
            

    # Lee la orientación del BNO055
    orientacion = bno.euler

    # Convierte la orientación a un valor de error para el controlador PID
    error = target - orientacion[1]

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

    # Escribe el valor en el MCP4725
    dac.value = valor

    # Enviar los datos a Node-RED
    #payload = {"angulo": orientacion[1], "output": u, "referencia": target}
    payload = {"topic": "medido", "payload": orientacion[1]}, {"topic": "referencia", "payload": target}, {"topic": "presion", "payload": u}

    client.loop()
    client.publish(topic, json.dumps(payload))

    print(t)

    # Espera un segundo antes de volver a leer la orientación del BNO055
    time.sleep(0.05)
