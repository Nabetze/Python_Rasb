

# Librerias del MQTT:
import paho.mqtt.client as mqtt
import numpy as np
#import pandas as pd


# Configuración del cliente MQTT
MQTT_BROKER = "10.100.236.192"
MQTT_TOPIC = "datos/bno055"

# Datos iniciales:
global gData
gData = np.array([])

# Función que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):

    global gData

    mensaje_decodificado = message.payload.decode("utf-8")
    angulo = float(mensaje_decodificado)
    gData = np.append(gData, angulo)

    if len(gData) > 200:
        gData = np.delete(gData, 0)

    #df = pd.DataFrame(data = gData)

    # Guardar el DataFrame en un archivo CSV
    #df.to_csv('Test.csv', index=False)

    print(angulo)


# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_forever()