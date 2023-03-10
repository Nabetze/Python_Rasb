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

limite = 30.0  #[kPA], máxima presion en el regulador electronico.
u = 0.0        #[kPa], valor inicial de la ley de control.

# Configura las constantes del controlador PID
kp = 1.0
ki = 0.0
kd = 0.0
prev_error = 0.0
integral = 0.0

# Configura el valor objetivo del controlador PID
target = 40.0

# Configurar el cliente MQTT
client = mqtt.Client()
client.connect("test.mosquitto.org", 1883, 60)

# Definir el tema MQTT
topic = "Control"

while True:
    # Lee la orientación del BNO055
    orientacion = bno.euler

    # Convierte la orientación a un valor de error para el controlador PID
    error = target - orientacion[2]

    # Calcula los términos proporcional, integral y derivativo del controlador PID
    proporcional = kp * error
    integral += ki * error
    derivativo = kd * (error - prev_error) / 0.05
    prev_error = error

    # Calcula el valor de salida del controlador PID
    u = proporcional + integral + derivativo

    # Limita la salida a los límites del regulador electrónico (0-[limite])
    u = min(max(u, 0), limite)

    # Convierte el voltaje a un valor de 12 bits para el MCP4725
    valor = int( u / limite * 4095)

    # Escribe el valor en el MCP4725
    dac.value = valor

    # Enviar los datos a Node-RED
    payload = {"error": error, "output": u}
    client.publish(topic, json.dumps(payload))

    print("Error: {:.2f} degrees, Presion: {:.2f} kPa".format(error, u))

    # Espera un segundo antes de volver a leer la orientación del BNO055
    time.sleep(0.05)
