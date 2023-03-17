import paho.mqtt.client as mqtt
import time

# Ganancias iniciales del controlador PID
Kp = 1.0
Ki = 0.0
Kd = 0.0

# Función para actualizar las ganancias del controlador PID
def update_Kp(new_Kp):
    global Kp
    Kp = new_Kp
    print("New gains: Kp={}".format(Kp))

# Función para actualizar las ganancias del controlador PID
def update_Ki(new_Ki):
    global Ki
    Ki = new_Ki
    print("New gains: Ki={}".format(Ki))

# Función para actualizar las ganancias del controlador PID
def update_Kd(new_Kd):
    global Kd
    Kd = new_Kd
    print("New gains: Kd={}".format(Kd))

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    global Kp, Ki, Kd
    print("Message received: topic={}, payload={}".format(message.topic, message.payload))

    # Vemos que tópico es:
    if message.topic == "Kp":
        # Se recibieron nuevas ganancias, se actualizan en el controlador PID
        gain = message.payload.decode("utf-8")
        update_Kp(float(gain))

    elif message.topic == "Ki":
        # Se recibieron nuevas ganancias, se actualizan en el controlador PID
        gain = message.payload.decode("utf-8")
        update_Ki(float(gain))

    elif message.topic == "Kd":
        # Se recibieron nuevas ganancias, se actualizan en el controlador PID
        gain = message.payload.decode("utf-8")
        update_Kd(float(gain))

# Configuración del cliente MQTTs
client = mqtt.Client()
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 60)

# Se suscribe al tema "pid/gains"
client.subscribe("Kp")
client.subscribe("Ki")
client.subscribe("Kd")

# Bucle principal
while True:
    client.loop()
    # Aquí se ejecuta el código del controlador PID con las ganancias actuales
    time.sleep(0.1)
