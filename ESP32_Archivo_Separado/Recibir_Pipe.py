import os

# Crear una tubería
pipe_read, pipe_write = os.pipe()

while True:
        # Leer los valores de la tubería
        data = os.read(pipe_read, 1024).decode()
        if data:
            # Separar los valores de la curva de referencia y del valor medido
            orientacion, target, u = map(float, data.strip().split(","))

            print()
            
