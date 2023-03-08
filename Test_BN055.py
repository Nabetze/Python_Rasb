import board
import busio
import adafruit_bno055

# Inicializar el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializar el sensor BNO055
sensor = adafruit_bno055.BNO055(i2c)

# Leer los datos del sensor
while True:
    heading, roll, pitch = sensor.euler

    # Imprimir los datos
    print("Heading: {:.2f} degrees, Roll: {:.2f} degrees, Pitch: {:.2f} degrees".format(heading, roll, pitch))
