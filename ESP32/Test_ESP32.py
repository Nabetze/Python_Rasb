import socket
import json

SERVER_IP = "192.168.18.42"  # Coloca la dirección IP de la Raspberry Pi aquí
SERVER_PORT = 8000  # Coloca el número de puerto utilizado en el ESP32 aquí

# Crea un objeto socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta el socket al servidor
sock.connect((SERVER_IP, SERVER_PORT))

while True:
    # Recibe los datos del ángulo desde el ESP32
    data = sock.recv(1024)

    # Decodifica los datos recibidos
    decoded_data = data.decode("utf-8")

    # Convierte los datos en un objeto JSON
    json_data = json.loads(decoded_data)

    # Accede al valor del ángulo en el objeto JSON
    angle = json_data["angle"]

    # Imprime el ángulo recibido
    print("Ángulo: ", angle)

# Cierra el socket
sock.close()
