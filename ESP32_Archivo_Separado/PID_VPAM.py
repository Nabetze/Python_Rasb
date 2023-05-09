# Archivo donde está la clase PID.

class PID:

    # Colocamos un nombre al controlador
    def __init__(self, name):
        # Name:
        self.name = name

        # Inicializamos las ganancias del PID
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0
       
        # Measured:
        self.angulo = 0
        self.prev_error = 0.0
        self.error = 0

        # Control initial values:
        self.proporcional = 0
        self.integral = 0
        self.derivativo = 0

        # Output settings:
        # Raspberry max Output (In case we connect the DAC directly to the raspberry)
        self.Vol_rasp = 5.4  #Vol.
        self.limite = 30.0  #[kPA], máxima presion en el regulador electronico.
        self.u = 0.0        #[kPa], valor inicial de la ley de control.


    # Actualizamos los valores de las ganancias:

    def Kp_update(self, Kp_value):
        self.Kp = Kp_value

    def Ki_update(self, Ki_value):
        self.Ki = Ki_value

    def Kd_update(self, Kd_value):
        self.Kd = Kd_value

    def Gain_update (self, Gains):
        # The input is a list [Kp, Ki, Kd]:

        self.Kd = Gains[0]
        self.Ki = Gains[1]
        self.Kp = Gains[2]

    def Calculate_u (self, actual_angle, target):

        # Lee la orientación del BNO055
        self.angle = actual_angle

        # Convierte la orientación a un valor de error para el controlador PID
        self.error = round(target - self.angle, 2)

        # Calcula los términos proporcional, integral y derivativo del controlador PID
        self.proporcional = round(self.Kp * self.error, 2)
        self.integral = round(self.integral + self.Ki * self.error, 2)
        self.derivativo = round(self.Kp * (self.error - self.prev_error) / 0.05, 2)

        self.prev_error = round(self.error, 2)

        # Calcula el valor de salida del controlador PID [kPa]
        self.u = round(self.proporcional + self.integral + self.derivativo, 2)

        # Limita la salida a los límites del regulador electrónico (0-[limite])
        self.u = min(max(self.u, 0), self.limite)    

    def Send_u (self, pressure, topic, mqttClient):

        # Send by MQTT protocol.
        mqttClient.publish(topic, pressure)

    def Stop_Controll(self):

        # All values to zero:
        self.u = 0

        self.angulo = 0
        self.prev_error = 0.0
        self.error = 0

        # Control initial values:
        self.proporcional = 0
        self.integral = 0
        self.derivativo = 0