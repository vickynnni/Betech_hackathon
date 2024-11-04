import random

class Truck:
    def __init__(self, battery_capacity, charging_ports, charging_speed):
        self.battery_capacity = battery_capacity
        self.charging_ports = charging_ports  # Listado de puntos de carga, por ejemplo ['top', 'right']
        self.charging_speed = charging_speed  # Límite de velocidad de carga en kW

    def __str__(self):
        return f"Truck: Battery Capacity - {self.battery_capacity}, Charging Ports - {', '.join(self.charging_ports)}, Charging Speed - {self.charging_speed}"


class GrupoIsleta:
    def __init__(self, n_isletas, charge_power, charging_ports):
        self.charge_power = charge_power
        self.charging_ports = charging_ports
        self.trucks = []
        self.n_isletas = n_isletas

    def __str__(self):
        return f"Isleta: Charge Power - {self.charge_power}, Charging Ports - {', '.join(self.charging_ports)}, Occupied - {self.occupied}, N Isletas - {self.n_isletas}"
    
    def get_free_spaces(self):
        return self.n_isletas-len(self.trucks)
    
    def occupy(self,truck: Truck):
        if(len(self.trucks) < self.n_isletas):
            self.trucks.append(truck)
            return True
        return False
    
    def get_trucks(self):
        return self.trucks

    def free(self,truck):
        if(self.occupied > 0):
            self.occupied -=1
            return True
        return False

def get_trucks(n):
    # Crear 100 camiones con valores aleatorios
    random.seed(10)
    trucks = []
    for _ in range(n):
        # Generar valores aleatorios
        battery_capacity = random.randint(100, 500)  # Capacidad de 100 a 500 kWh
        charging_ports = random.sample(['top', 'right', 'left', 'inductive'], k=random.randint(1, 4))  # 1 a 4 puertos de carga
        charging_speed = random.randint(20, 250)  # Velocidad de carga entre 50 y 200 kW

        # Crear y agregar el camión a la lista
        truck = Truck(battery_capacity, charging_ports, charging_speed)
        trucks.append(truck)
    return trucks

def check_finished(trucks):

def main():
    # Construir estructuras
    [truck1, truck2] = [Truck(100, ['top', 'right'], 50), Truck(200, ['top', 'left'], 100)]
    print(truck1)
    print(truck2)
    isletas = []
    isletas.append(Isleta(5, 250, ['right', 'left', 'top']))
    isletas.append(Isleta(7, 150, ['right', 'top']))
    isletas.append(Isleta(3, 110, ['top', 'inductive']))
    isletas.append(Isleta(5, 60, ['left','top','inductive']))
    trucks = get_trucks(10)
    
    t=0 # Tiempo s
    t_multiplier = 1/3600
    finished=False
    # Proceso principal
    #Ordenar por menor capacidad de batería
    trucks_ordered = sorted(trucks, key=lambda x: x.battery_capacity, reverse=False)
    print(trucks_ordered)
    while(not finished):
        t += 1
        free_space=True
        for isleta in isletas:
            if(isleta.get_free_spaces() > 0):
                if(isleta.occupy(truck)):
                    break
            else:
                continue


        
        


if __name__ == "__main__":
    main()

def time_spent(charge_power, battery_capacity, inductive):
    if(inductive):
        charge_power = charge_power * 0.7
    return battery_capacity / charge_power