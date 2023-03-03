import serial

port = "/dev/ttyACM0"

ser = serial.Serial(port, 115200, timeout=1)

while True:
    data = ser.readline()
    data_sensor = data.decode()

    print(data_sensor)