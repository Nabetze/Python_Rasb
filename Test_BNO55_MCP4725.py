import time
import board
import busio
import adafruit_bno055
import adafruit_mcp4725

# Inicializa el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

print(i2c[0])
print(i2c[1])

# Inicializa el BNO055
bno = adafruit_bno055.BNO055(i2c)

# Inicializa el MCP4725
dac = adafruit_mcp4725.MCP4725(i2c)
