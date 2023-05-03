import paho.mqtt.client as mqtt

# Define las credenciales de conexión MQTT
# Configuración del cliente MQTT
MQTT_BROKER = "10.100.239.29" #"192.168.18.42" 
MQTT_TOPIC = "datos/bno055"

# Conecta al servidor MQTT
# Configuración del cliente MQTT
mqttClient = mqtt.Client()
mqttClient.connect(MQTT_BROKER, 1883)
mqttClient.subscribe(MQTT_TOPIC)
mqttClient.loop_start()

# Publica el valor decimal en el tópico "miTopico"
valor_decimal = 1.23
mqttClient.publish("datos/u", valor_decimal)

# Desconecta del servidor MQTT
mqttClient.disconnect()
