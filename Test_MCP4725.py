# Codigo para enviar voltaje manualmente.

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

while True:
    
    # Calcula el valor de salida del controlador PID
    u = int(input("Ingresar valor de voltaje: "))

    # Limita la salida a los límites del regulador electrónico (0-[limite])
    #u = min(max(u, 0), 5)

    # Convierte el voltaje a un valor de 12 bits para el MCP4725
    valor = int( u / 5 * 65535)

    # Escribe el valor en el MCP4725
    dac.value = valor

    print("El voltaje que se envió fue: {}".format(valor*5/65535))

    # Espera un segundo antes de volver a leer la orientación del BNO055

