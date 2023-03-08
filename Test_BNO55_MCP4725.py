import time
import board
import busio
import adafruit_bno055
import adafruit_mcp4725

# Inicializa el primer bus I2C para el BNO055
i2c_bno = busio.I2C(board.SCL, board.SDA)

# Inicializa el BNO055 con la dirección I2C predeterminada
bno = adafruit_bno055.BNO055(i2c_bno)

# Inicializa el segundo bus I2C para el MCP4725
i2c_dac = busio.I2C(board.SCL_1, board.SDA_1)

# Inicializa el MCP4725 con la dirección I2C predeterminada
dac = adafruit_mcp4725.MCP4725(i2c_dac)

while True:
    # Lee la orientación del BNO055
    orientacion = bno.euler

    # Convierte la orientación a un valor de voltaje para el MCP4725
    voltaje = orientacion[0] / 360 * 3.3

    # Convierte el voltaje a un valor de 12 bits para el MCP4725
    valor = int(voltaje / 3.3 * 4095)

    # Escribe el valor en el MCP4725
    dac.value = valor

    # Imprime la orientación y el valor de voltaje en la consola
    print("Orientación (heading, roll, pitch): {}".format(orientacion))
    print("Valor de voltaje escrito en el MCP4725: {:.2f} V".format(valor / 4095 * 3.3))

    # Espera un segundo antes de volver a leer la orientación del BNO055
    time.sleep(1)
