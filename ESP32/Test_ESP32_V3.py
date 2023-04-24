# tESTEANDO SI LLEGA RAPIDO.
import socket

HOST = '10.100.232.87'  # Cambiar por la dirección IP de la Raspberry Pi
PORT = 1234

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Conexión establecida desde', addr)
        while True:
            data = conn.recv(8)  # Recibe los datos (7 caracteres + 1 byte de suma de comprobación)
            if not data:
                break
            num_str = data[:-1].decode('utf-8')  # Convierte la cadena de bytes a una cadena de caracteres
            checksum = data[-1]  # Obtiene el byte de suma de comprobación
            sum = 0
            for byte in data[:-1]:
                sum += byte
            if checksum != sum % 256:  # Verifica el byte de suma de comprobación
                print('Error en la transmisión. Se solicita una retransmisión.')
                conn.sendall(b'Error')
            else:
                num = float(num_str)
                print('Número recibido:', num)
                conn.sendall(b'OK')
