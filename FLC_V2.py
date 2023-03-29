# Se agrega la opción de crear la MF con los rangos equilateros en funcion de dos valores.
# Se envia el numero de ciclos a Node-Red
# Definir los tiempos de trabajo manualmente con nodered.-


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

# Limites de los MF.
lim_inf_e = -30
lim_sup_e = 30
t_e = (lim_sup_e - lim_inf_e)/6 # Porque numero de conjuntos difusos.

error = ctrl.Antecedent(np.arange(lim_inf_e, lim_sup_e, 0.01), 'error')
error['NG'] = fuzz.trimf(error.universe, [lim_inf_e - t_e, lim_inf_e, lim_inf_e + t_e])
error['NM'] = fuzz.trimf(error.universe, [lim_inf_e, lim_inf_e + t_e, lim_inf_e + 2*t_e])
error['NP'] = fuzz.trimf(error.universe, [lim_inf_e + t_e, lim_inf_e + 2*t_e, lim_inf_e + 3*t_e])
error['Z']  = fuzz.trimf(error.universe, [lim_inf_e + 2*t_e, lim_inf_e + 3*t_e, lim_inf_e + 4*t_e])
error['PP'] = fuzz.trimf(error.universe, [lim_inf_e + 3*t_e, lim_inf_e + 4*t_e, lim_inf_e + 5*t_e])
error['PM'] = fuzz.trimf(error.universe, [lim_inf_e + 4*t_e, lim_inf_e + 5*t_e, lim_inf_e + 6*t_e])
error['PG'] = fuzz.trimf(error.universe, [lim_inf_e + 5*t_e, lim_inf_e + 6*t_e, lim_inf_e + 7*t_e])

lim_inf_de = -1000
lim_sup_de = 1000
t_de = (lim_sup_de - lim_inf_de)/6 # Porque numero de conjuntos difusos.

derror = ctrl.Antecedent(np.arange(lim_inf_de, lim_sup_de, 0.01), 'derror')
derror['NG'] = fuzz.trimf(derror.universe, [lim_inf_de -    t_de,lim_inf_de         , lim_inf_de +   t_de])
derror['NM'] = fuzz.trimf(derror.universe, [lim_inf_de         , lim_inf_de +   t_de, lim_inf_de + 2*t_de])
derror['NP'] = fuzz.trimf(derror.universe, [lim_inf_de +   t_de, lim_inf_de + 2*t_de, lim_inf_de + 3*t_de])
derror['Z']  = fuzz.trimf(derror.universe, [lim_inf_de + 2*t_de, lim_inf_de + 3*t_de, lim_inf_de + 4*t_de])
derror['PP'] = fuzz.trimf(derror.universe, [lim_inf_de + 3*t_de, lim_inf_de + 4*t_de, lim_inf_de + 5*t_de])
derror['PM'] = fuzz.trimf(derror.universe, [lim_inf_de + 4*t_de, lim_inf_de + 5*t_de, lim_inf_de + 6*t_de])
derror['PG'] = fuzz.trimf(derror.universe, [lim_inf_de + 5*t_de, lim_inf_de + 6*t_de, lim_inf_de + 7*t_de])


lim_inf_u = 0
lim_sup_u = 10
t_u = (lim_sup_u - lim_inf_u)/6 # Porque numero de conjuntos difusos.

voltaje = ctrl.Consequent(np.arange(lim_inf_u, lim_sup_u, 0.1), 'voltaje')
voltaje['NG'] = fuzz.trimf(voltaje.universe, [lim_inf_u -    t_u,lim_inf_u        , lim_inf_u +   t_u])
voltaje['NM'] = fuzz.trimf(voltaje.universe, [lim_inf_u         ,lim_inf_u +   t_u, lim_inf_u + 2*t_u])
voltaje['NP'] = fuzz.trimf(voltaje.universe, [lim_inf_u +   t_u, lim_inf_u + 2*t_u, lim_inf_u + 3*t_u])
voltaje['Z']  = fuzz.trimf(voltaje.universe, [lim_inf_u + 2*t_u, lim_inf_u + 3*t_u, lim_inf_u + 4*t_u])
voltaje['PP'] = fuzz.trimf(voltaje.universe, [lim_inf_u + 3*t_u, lim_inf_u + 4*t_u, lim_inf_u + 5*t_u])
voltaje['PM'] = fuzz.trimf(voltaje.universe, [lim_inf_u + 4*t_u, lim_inf_u + 5*t_u, lim_inf_u + 6*t_u])
voltaje['PG'] = fuzz.trimf(voltaje.universe, [lim_inf_u + 5*t_u, lim_inf_u + 6*t_u, lim_inf_u + 7*t_u])

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
Num_ciclos = -1

# Limite de ciclos:
Lim_ciclos = 0

# Función para actualizar las ganancias del controlador PID
def update_ciclos(new_Lim_ciclos):
    global Lim_ciclos
    global Num_ciclos
    Lim_ciclos = new_Lim_ciclos
    # Colocamos 0 para que inicie el bucle
    Num_ciclos = 0
    print("Numero de ciclos recibido: Num_ciclos={}".format(Lim_ciclos))


# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    print("Mensaje recibido: topic={}, payload={}".format(message.topic, message.payload))

    # Vemos que tópico es:
    if message.topic == "Ciclos":
        # Se recibieron nuevo numero de ciclos
        gain = message.payload.decode("utf-8")
        update_ciclos(float(gain))


# Configurar el cliente MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
#client.connect("test.mosquitto.org", 1883, 60)

# Se suscribe al tema:
client.subscribe("Ciclos")
client.subscribe("tsubida")
client.subscribe("tbajada")
client.subscribe("testatico")
client.subscribe("tinicial")

# Definir el tema MQTT
topic = "Control"

# Tiempo inicial:
t_inicial = time.time()
t_anterior = time.time() - t_inicial

while True:

    # Paramos el sistema si es que el número de ciclos llegó al límite:
    if Num_ciclos == -1:
    
        # Volvemos la referencia 0.
        target = 0

        # Apagamos el regulador electrónico
        u = 0

        # Lee la orientación del BNO055
        orientacion = bno.euler

        # Volvemos 0 tanto al error como la derivada del error:
        error_medido = 0
        derror_medido = 0
 
        # Restauramos los valores iniciales:
        t1 = tinicial
        t2 = tsubida + t1
        t3 = testatico + t2
        t4 = tbajada + t3

        # Actualizamos el t_inicial y reseteamos los otros tiempos: 
        t_inicial = time.time()
        t_anterior = time.time() - t_inicial

    else:

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
        orientacion = bno.euler

        # Convierte la orientación a un valor de error para el controlador PID
        error_medido = target - orientacion[1]

        # Calculamos la derivada del error:
        derror_medido = (error_medido - error_medido_anterior)/(t - t_anterior)
        t_anterior = t
        
        # Actualiza los valores de entrada del controlador difuso y saturamos:
        simulacion.input['error'] = min(max(round(error_medido, 2), -30), 30)
        simulacion.input['derror'] = min(max(round(derror_medido, 2), -75), 75)
        

        #print('Medido:{:2f} U:{:2f} Error:{:2f} Derror:{:2f} dt: {:2f}'.format(orientacion[1], u, error_medido, derror_medido, t - t_anterior))

        # Evalúa la salida del controlador difuso
        simulacion.compute()
        
        # Obtiene la salida del controlador difuso
        voltaje_regulador = simulacion.output['voltaje']

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
    payload = {"topic": "medido", "payload": orientacion[1]}, {"topic": "referencia", "payload": target}, {"topic": "presion", "payload": u}, {"topic": "ciclos", "payload": Num_ciclos}

    client.loop()
    print(orientacion[1])
    client.publish(topic, json.dumps(payload))

    # Espera un segundo antes de volver a leer la orientación del BNO055
    time.sleep(0.05)
