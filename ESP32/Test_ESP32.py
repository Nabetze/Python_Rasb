import socket
import json

HOST = '' # Escucha todas las interfaces de red
PORT = 8888 # Puerto al que el ESP32 se conecta

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

print("Esperando conexión...")
conn, addr = s.accept()
print("Conectado por", addr)

while True:
    data = conn.recv(1024)
    if not data:
        break
    json_data = json.loads(data.decode())
    angle = json_data["angle"]
    print("Ángulo:", angle)
    