import paho.mqtt.client as mqtt
import time

# Ganancias iniciales del controlador PID
Kp = 1.0
Ki = 0.0
Kd = 0.0

# Función para actualizar las ganancias del controlador PID
def update_gains(new_Kp, new_Ki, new_Kd):
    global Kp, Ki, Kd
    Kp = new_Kp
    Ki = new_Ki
    Kd = new_Kd
    print("New gains: Kp={}, Ki={}, Kd={}".format(Kp, Ki, Kd))

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    global Kp, Ki, Kd
    print("Message received: topic={}, payload={}".format(message.topic, message.payload))
    if message.topic == "pid/gains":
        # Se recibieron nuevas ganancias, se actualizan en el controlador PID
        gains = message.payload.decode("utf-8").split(",")
        update_gains(float(gains[0]), float(gains[1]), float(gains[2]))

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 60)

# Se suscribe al tema "pid/gains"
client.subscribe("Kp")

# Bucle principal
while True:
    client.loop()
    # Aquí se ejecuta el código del controlador PID con las ganancias actuales
    time.sleep(0.1)
