import time
import board
import busio
import adafruit_bno055
import adafruit_mcp4725

# Inicializa el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializa el BNO055
bno = adafruit_bno055.BNO055(i2c[0])

# Inicializa el MCP4725
dac = adafruit_mcp4725.MCP4725(i2c[1])
