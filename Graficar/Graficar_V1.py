import matplotlib.pyplot as plt
import numpy as np
import time


import socket

HOST = '192.168.43.101'
PORT = 1234

fig, ax = plt.subplots()    


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

            
            ax.clear()
            ax.plot(num, 'r', label='Angulo')
            ax.set_xlabel('Muestras')
            ax.set_ylabel('Ángulo (grados)')
            ax.set_ylim(-180, 180)  

            plt.pause(1)


