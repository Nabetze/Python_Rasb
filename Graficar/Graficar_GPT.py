import tkinter as tk
import paho.mqtt.client as mqtt

# Configuración del cliente MQTT
MQTT_SERVER = "10.100.236.192"
MQTT_PORT = 1883
MQTT_TOPIC = "datos/bno055"

# Función que se llama cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    # Actualiza el valor de la etiqueta de texto con el mensaje recibido
    angle_label.config(text=message.payload.decode())

# Configuración de la ventana de GUI
root = tk.Tk()
root.title("Sensor BNO055")

# Etiqueta de texto que muestra el ángulo actual
angle_label = tk.Label(root, font=("Helvetica", 72), text="0.00")
angle_label.pack()

# Conexión a MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_SERVER, MQTT_PORT)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.on_message = on_message
mqtt_client.loop_start()

# Función principal de la GUI
def main():
    root.mainloop()

if __name__ == '__main__':
    main()
