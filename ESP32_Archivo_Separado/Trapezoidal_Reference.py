# Clase donde defino la clase trapezoidal.

# Creamos una clase de la referencia:
class Trapezoidal_Reference:

    # Le colocamos un nombre:
    def __init__(self, name):
        self.name = name

        # Default time limits:
        self.tsubida = 3    # t2 - t1
        self.tbajada = 5    # t4 - t3
        self.testatico = 5  # t3 - t2
        self.tinicial = 5   # t1

        # Default angle limits:
        self.Amax = 60
        self.Amin = 50

        # Points of time:
        self.t1 = self.tinicial
        self.t2 = self.tsubida + self.t1
        self.t3 = self.testatico + self.t2
        self.t4 = self.tbajada + self.t3

        # Number of cicles:
        self.Num_ciclos = -1

        self.Lim_ciclos = 0

        self.ttotal = self.tsubida + self.tbajada + self.testatico + self.tinicial

    def Update_angle_limits (self, Max, Min):
        # Limit in degrees
        self.Amax = Max
        self.Amin = Min

    def Update_Tsubida (self, Tsubida):

        self.tsubida = Tsubida
        # Update the total duration:
        self.ttotal = self.tsubida + self.tbajada + self.testatico + self.tinicial

    def Update_Tbajada (self, Tbajada):

        self.tbajada = Tbajada
        # Update the total duration:
        self.ttotal = self.tsubida + self.tbajada + self.testatico + self.tinicial

    def Update_Testatico (self, Testatico):

        self.testatico = Testatico
        # Update the total duration:
        self.ttotal = self.tsubida + self.tbajada + self.testatico + self.tinicial

    def Update_Tinicio (self, Tinicio):

        self.tinicial = Tinicio
        # Update the total duration:
        self.ttotal = self.tsubida + self.tbajada + self.testatico + self.tinicial
        
    def Restart_points_of_time(self):
        self.t1 = self.tinicial
        self.t2 = self.tsubida + self.t1
        self.t3 = self.testatico + self.t2
        self.t4 = self.tbajada + self.t3

    def Update_points_of_time(self):
        self.t1 = self.tinicial
        self.t2 = self.tsubida + self.t1
        self.t3 = self.testatico + self.t2
        self.t4 = self.tbajada + self.t3

    def Update_limit_of_time(self):
        # Actualizamos los límites:
        self.t1 = self.t1 + self.ttotal
        self.t2 = self.t2 + self.ttotal
        self.t3 = self.t3 + self.ttotal
        self.t4 = self.t4 + self.ttotal

    def Compute_target(self, time):

        # Lower part:
        if time <= self.t1:
                
            target = self.Amin
                
        # Rising part:
        elif time <= self.t2:
                
            a = (self.Amax - self.Amin)/(self.tsubida)
                
            target = round(a*(time - self.t2) + self.Amax, 2)
                
        # Upper part:
        elif time <= self.t3:
                
            target = self.Amax
                
        # Falling part:
        elif time <= self.t4:
                
            c = (self.Amin - self.Amax)/(self.tbajada)
                
            target = round(c*(time - self.t3) + self.Amax, 2)
                
        # Lower part again:
        else:
                
            target = self.Amin
                
            # Actualizamos los límites:
            self.Update_limit_of_time()
                
            # Sumamos un ciclo:
            self.Num_ciclos += 1

            # Si llegamos al último ciclo entonces "apagamos todo":
            if self.Num_ciclos == self.Lim_ciclos:
                self.Num_ciclos = -1

        return target
