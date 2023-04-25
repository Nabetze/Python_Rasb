# Este si recibe sin problemas pero a veces recibe datos incorrectos.

import socket

HOST = '192.168.43.101'
PORT = 1234

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Esperando conexión...')
    conn, addr = s.accept()
    with conn:
        print('Conexión establecida por', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            num = int.from_bytes(data, byteorder='little')
            print(num)
