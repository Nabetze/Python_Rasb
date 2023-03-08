import time
import board
import busio
import adafruit_bno055
import adafruit_mcp4725

# Inicializa el bus I2C
i2c = board.I2C()


print(i2c)