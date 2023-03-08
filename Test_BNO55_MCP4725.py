import time
import board
import busio
import adafruit_mcp4725
import adafruit_bno055

# Configuramos el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Creamos un objeto MCP4725 sin argumentos
dac = adafruit_mcp4725.MCP4725(i2c)

# Creamos un objeto BNO055 sin argumentos
sensor = adafruit_bno055.BNO055(i2c)

# Configuramos la salida del DAC
dac.normalized_value = 0.5

# Leemos los valores de Euler del BNO055
while True:
    heading, roll, pitch = sensor.euler

    # Convertimos los valores a grados
    heading_deg = heading % 360.0
    roll_deg = roll
    pitch_deg = pitch

    # Imprimimos los valores
    print("Heading: {0:.2f} degrees, Roll: {1:.2f} degrees, Pitch: {2:.2f} degrees".format(heading_deg, roll_deg, pitch_deg))

    # Esperamos 1 segundo antes de leer los valores de nuevo
    time.sleep(1.0)
