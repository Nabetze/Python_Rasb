import time
import board
import busio
import adafruit_bno055
import adafruit_mcp4725

# Inicializa el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializa el BNO055 en la dirección 0x28
bno = adafruit_bno055.BNO055_I2C(i2c, address=0x28)

# Inicializa el MCP4725 en la dirección 0x60
dac = adafruit_mcp4725.MCP4725(i2c, address=0x60)

float limite = 30  #[kPA], máxima presion en el regulador electronico.
float u = 0        #[kPa], valor inicial de la ley de control.

while True:
    # Lee la orientación del BNO055
    orientacion = bno.euler

    # Valor de presión:


    # Convierte el voltaje a un valor de 12 bits para el MCP4725
    valor = int( u / limite * 4095)

    # Escribe el valor en el MCP4725
    dac.value = valor

    # Imprime la orientación y el valor de voltaje en la consola
    print("Orientación (heading, roll, pitch): {}".format(orientacion))
    print("Valor de voltaje escrito en el MCP4725: {:.2f} V".format(valor / 4095 * 5))

    # Espera un segundo antes de volver a leer la orientación del BNO055
    time.sleep(0.1)