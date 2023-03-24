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
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

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

# Colocar aca el controlador a utilizar: -------------------------------------
# Configura las constantes del controlador Fuzzy, entradas y salidas:
error = ctrl.Antecedent(np.arange(-30, 30, 0.01), 'error')
error['NG'] = fuzz.trapmf(error.universe, [-58.2, -38.22, -29.6, -20.72])
error['NM'] = fuzz.trimf(error.universe,  [-30, -20, -9.99])
error['NP'] = fuzz.trimf(error.universe, [-20, -9.99, 0])
error['Z'] = fuzz.trimf(error.universe, [-9.99, 0, 9.99])
error['PP'] = fuzz.trimf(error.universe, [0, 9.99, 20])
error['PM'] = fuzz.trimf(error.universe, [9.99, 20, 30])
error['PG'] = fuzz.trapmf(error.universe, [21.43, 30, 45.6, 47.4])

derror = ctrl.Antecedent(np.arange(-75, 75, 0.01), 'derror')
derror['NG'] = fuzz.trapmf(derror.universe,  [-145.5, -95.55, -73.98, -51.81])
derror['NM'] = fuzz.trimf(derror.universe,   [-75, -49.98, -24.99])
derror['NP'] = fuzz.trimf(derror.universe,  [-49.98, -24.99, 0])
derror['Z']  = fuzz.trimf(derror.universe,  [-24.99, 0, 24.99])
derror['PP'] = fuzz.trimf(derror.universe, [0, 24.99, 50.01])
derror['PM'] = fuzz.trimf(derror.universe, [24.99, 50.01, 75])
derror['PG'] = fuzz.trapmf(derror.universe, [53.58, 75, 114, 118.5])

voltaje = ctrl.Consequent(np.arange(0, 10, 0.1), 'voltaje')
voltaje['NG'] = fuzz.trapmf(voltaje.universe, [-19.4, -12.74, -9.86, -6.90])
voltaje['NM'] = fuzz.trimf(voltaje.universe, [-10, -6.66, -3.33])
voltaje['NP'] = fuzz.trimf(voltaje.universe, [-6.66, -3.33, 0])
voltaje['Z'] = fuzz.trimf(voltaje.universe, [-3.33, 0, 3.33])
voltaje['PP'] = fuzz.trimf(voltaje.universe, [0, 3.33, 6.66])
voltaje['PM'] = fuzz.trimf(voltaje.universe, [3.33, 6.66, 10])
voltaje['PG'] = fuzz.trapmf(voltaje.universe, [7.14, 10, 15.2, 15.8])

# Reglas:
regla1 = ctrl.Rule(error['NG'] & derror['NG'], voltaje['NG'])
regla2 = ctrl.Rule(error['NG'] & derror['NM'], voltaje['NG'])
regla3 = ctrl.Rule(error['NG'] & derror['NP'], voltaje['NG'])
regla4 = ctrl.Rule(error['NG'] & derror['Z'], voltaje['NG'])
regla5 = ctrl.Rule(error['NG'] & derror['PP'], voltaje['NM'])
regla6 = ctrl.Rule(error['NG'] & derror['PM'], voltaje['NP'])
regla7 = ctrl.Rule(error['NG'] & derror['PG'], voltaje['Z'])
regla8 = ctrl.Rule(error['NM'] & derror['NG'], voltaje['NG'])
regla9 = ctrl.Rule(error['NM'] & derror['NM'], voltaje['NG'])
regla10 = ctrl.Rule(error['NM'] & derror['NP'], voltaje['NG'])
regla11 = ctrl.Rule(error['NM'] & derror['Z'], voltaje['NM'])
regla12 = ctrl.Rule(error['NM'] & derror['PP'], voltaje['NP'])
regla13 = ctrl.Rule(error['NM'] & derror['PM'], voltaje['Z'])
regla14 = ctrl.Rule(error['NM'] & derror['PG'], voltaje['PP'])
regla15 = ctrl.Rule(error['NP'] & derror['NG'], voltaje['NG'])
regla16 = ctrl.Rule(error['NP'] & derror['NM'], voltaje['NG'])
regla17 = ctrl.Rule(error['NP'] & derror['NP'], voltaje['NM'])
regla18 = ctrl.Rule(error['NP'] & derror['Z'], voltaje['NP'])
regla19 = ctrl.Rule(error['NP'] & derror['PP'], voltaje['Z'])
regla20 = ctrl.Rule(error['NP'] & derror['PM'], voltaje['PP'])
regla21 = ctrl.Rule(error['NP'] & derror['PG'], voltaje['PM'])
regla22 = ctrl.Rule(error['Z'] & derror['NG'], voltaje['NG'])
regla23 = ctrl.Rule(error['Z'] & derror['NM'], voltaje['NM'])
regla24 = ctrl.Rule(error['Z'] & derror['NP'], voltaje['NP'])
regla25 = ctrl.Rule(error['Z'] & derror['Z'], voltaje['Z'])
regla26 = ctrl.Rule(error['Z'] & derror['PP'], voltaje['PP'])
regla27 = ctrl.Rule(error['Z'] & derror['PM'], voltaje['PM'])
regla28 = ctrl.Rule(error['Z'] & derror['PG'], voltaje['PG'])
regla29 = ctrl.Rule(error['PP'] & derror['NG'], voltaje['NM'])
regla30 = ctrl.Rule(error['PP'] & derror['NM'], voltaje['NP'])
regla31 = ctrl.Rule(error['PP'] & derror['NP'], voltaje['Z'])
regla32 = ctrl.Rule(error['PP'] & derror['Z'], voltaje['PP'])
regla33 = ctrl.Rule(error['PP'] & derror['PP'], voltaje['PM'])
regla34 = ctrl.Rule(error['PP'] & derror['PM'], voltaje['PG'])
regla35 = ctrl.Rule(error['PP'] & derror['PG'], voltaje['PG'])
regla36 = ctrl.Rule(error['PM'] & derror['NG'], voltaje['NP'])
regla37 = ctrl.Rule(error['PM'] & derror['NM'], voltaje['Z'])
regla38 = ctrl.Rule(error['PM'] & derror['NP'], voltaje['PP'])
regla39 = ctrl.Rule(error['PM'] & derror['Z'], voltaje['PM'])
regla40 = ctrl.Rule(error['PM'] & derror['PP'], voltaje['PG'])
regla41 = ctrl.Rule(error['PM'] & derror['PM'], voltaje['PG'])
regla42 = ctrl.Rule(error['PM'] & derror['PG'], voltaje['PG'])
regla43 = ctrl.Rule(error['PG'] & derror['NG'], voltaje['Z'])
regla44 = ctrl.Rule(error['PG'] & derror['NM'], voltaje['PP'])
regla45 = ctrl.Rule(error['PG'] & derror['NP'], voltaje['PM'])
regla46 = ctrl.Rule(error['PG'] & derror['Z'], voltaje['PG'])
regla47 = ctrl.Rule(error['PG'] & derror['PP'], voltaje['PG'])
regla48 = ctrl.Rule(error['PG'] & derror['PM'], voltaje['PG'])
regla49 = ctrl.Rule(error['PG'] & derror['PG'], voltaje['PG'])

# Agregamos las reglas:
controlador = ctrl.ControlSystem([regla1, regla2, regla3, regla4, regla5, regla6, regla7, regla8, regla9
                                , regla10, regla11, regla12, regla13, regla14, regla15, regla16, regla17, regla18, regla19
                                , regla20, regla21, regla22, regla23, regla24, regla25, regla26, regla27, regla28, regla29
                                , regla30, regla31, regla32, regla33, regla34, regla35, regla36, regla37, regla38, regla39
                                , regla40, regla41, regla42, regla43, regla44, regla45, regla46, regla47, regla48, regla49])

# Creamos una simulacion:
simulacion = ctrl.ControlSystemSimulation(controlador)

# Variable del error:
error_medido_anterior = 0

# Creamos una variable integral:
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

# Tiempo inicial:
t_inicial = time.time()
t_anterior = time.time() - t_inicial

while True:

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
            

    # Lee la orientación del BNO055
    orientacion = bno.euler

    # Convierte la orientación a un valor de error para el controlador PID
    error_medido = target - orientacion[1]

    # Calculamos la derivada del error:
    derror_medido_ = (error_medido - error_medido_anterior)/(t - t_anterior)
    t_anterior = t
    
    # Actualiza los valores de entrada del controlador difuso
    controlador.input['error'] = error_medido
    controlador.input['derror'] = derror_medido_
    
    # Evalúa la salida del controlador difuso
    controlador.compute()
    
    # Obtiene la salida del controlador difuso
    voltaje_regulador = controlador.output['voltaje']

    # Calcula el valor de salida del controlador PID [kPa]
    u += voltaje_regulador

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


    # Espera un segundo antes de volver a leer la orientación del BNO055
    time.sleep(0.05)
