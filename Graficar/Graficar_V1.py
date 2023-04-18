import matplotlib.pyplot as plt
import numpy as np
import time

fig, ax = plt.subplots()    

def update_plot():
    # Aquí debes poner el código que obtiene los datos que quieres graficar
    x = np.arange(0, 10, 0.1)
    y = np.sin(x)
    # Actualiza el gráfico
    ax.clear()
    ax.plot(x, y)
    # Ajusta los límites de los ejes si es necesario
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 1)

while True:
    update_plot()
    plt.pause(0.1)