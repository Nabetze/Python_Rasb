import os

# Crear una tubería
pipe_in, pipe_out = os.pipe()

while True:
        # Leer los valores de la tubería
        data = os.read(pipe_in, 1024).decode()
        if data:
            # Separar los valores de la curva de referencia y del valor medido
            setpoint, valor_medido, valor_control = map(float, data.strip().split(","))
            
