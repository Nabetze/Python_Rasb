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
# Voltaje máximo de entrada:
Vol_rasp = 5.4  #Vol.


limite = 30.0  #[kPA], máxima presion en el regulador electronico.
u = 0.0        #[kPa], valor inicial de la ley de control.

# Configura las constantes del controlador PID
kp = 0.2
ki = 0.0
kd = 0.0
prev_error = 0.0
integral = 0.0

# Configura el valor objetivo del controlador PID
target = 40.0

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

# Frecuencia de muestreo de 0.1 segundos
dt = 0.1


while True:

    start_time = time.time()
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

    #print("Error: {:.2f} degrees, Presion: {:.2f} kPa".format(error, u))

    end_time = time.time()
    # Tiempo total de ejecución del código de control
    exec_time = end_time - start_time

    # Frecuencia real de control
    freq = 1 / (dt + exec_time)
    print("Frecuencia real: {:.2f} Hz y el tiempo de ejecución fue de: {:.2f}".format(freq, exec_time))

    # Espera un segundo antes de volver a leer la orientación del BNO055
    time.sleep(0.05)
