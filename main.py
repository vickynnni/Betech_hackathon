import random

class Truck:
    def __init__(self, battery_capacity, charging_ports, charging_speed):
        self.battery_capacity = battery_capacity
        self.current_battery = 0
        self.charging_ports = charging_ports  # Listado de puntos de carga, por ejemplo ['top', 'right']
        self.charging_speed = charging_speed  # Límite de velocidad de carga en kW

    def __str__(self):
        return f"Truck: Battery Capacity - {self.battery_capacity}, Charging Ports - {', '.join(self.charging_ports)}, Charging Speed - {self.charging_speed}"
    
    def is_full(self):
        return self.current_battery >= self.battery_capacity

    def charge(self, charge_power, time_increment):
        power_supplied = charge_power*time_increment
        self.current_battery += power_supplied
        return power_supplied

class GrupoIsleta:
    def __init__(self, n_isletas, charge_power, charging_ports):
        self.charge_power = charge_power
        self.charging_ports = charging_ports
        self.trucks = []
        self.n_isletas = n_isletas

    def __str__(self):
        return f"Isleta: Charge Power - {self.charge_power}, Charging Ports - {', '.join(self.charging_ports)}, Trucks - {len(self.trucks)}, Free Spaces - {self.get_free_spaces()}"
    
    def get_free_spaces(self):
        return self.n_isletas-len(self.trucks)
    
    def occupy(self,truck: Truck):
        if(len(self.trucks) < self.n_isletas):
            self.trucks.append(truck)
            return True
        return False
    
    def get_trucks(self):
        return self.trucks
    
    def set_trucks(self,trucks):
        self.trucks = trucks


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

def check_truck_isleta(truck: Truck, isleta: GrupoIsleta):
    for port in truck.charging_ports:
        if port in isleta.charging_ports:
            return True
    return False

def check_inductiva(truck: Truck, isleta: GrupoIsleta):
    #If the only common charging port is inductive, return True
    intersection = set(truck.charging_ports).intersection(set(isleta.charging_ports))
    if(len(intersection))==1 and 'inductive' in intersection:
        return True
    return False

def main():
    # Construir estructuras
    [truck1, truck2] = [Truck(100, ['top', 'right'], 50), Truck(200, ['top', 'left'], 100)]
    isletas = []
    isletas.append(GrupoIsleta(5, 250, ['right', 'left', 'top']))
    isletas.append(GrupoIsleta(7, 150, ['right', 'top']))
    isletas.append(GrupoIsleta(3, 110, ['top', 'inductive']))
    isletas.append(GrupoIsleta(5, 60, ['left','top','inductive']))
    trucks = get_trucks(100)
    
    t=0 # Tiempo s
    t_multiplier = 1
    finished=False
    # Proceso principal
    #Ordenar por menor capacidad de batería
    trucks_ordered = sorted(trucks, key=lambda x: x.charging_speed, reverse=False)
    # for t in trucks_ordered:
    #     print(str(t))
    t_increment = 1
    total_power_supplied = 0 #(kW*time)

    total_charging_power = 0
    for truck in trucks_ordered:
        total_charging_power += truck.battery_capacity
    print(f"Total charging power: {total_charging_power} kWh")

    #Rellenar isletas vacías
    for isleta in isletas:
            if(isleta.get_free_spaces() == 0):
                continue
            if(check_truck_isleta(trucks_ordered[0],isleta)):
                isleta.occupy(trucks_ordered[0])
                trucks_ordered.pop(0)
                continue

    # Bucle principal
    while(not finished):
        
        free_space=True
        #Cargar los camiones
        for isleta in isletas:
            trucks_isleta = isleta.get_trucks()
            trucks_isleta_new = []
            for truck in trucks_isleta:
                max_speed_truck = truck.charging_speed
                charge_power_isleta = isleta.charge_power
                inductive = check_inductiva(truck, isleta)
                effective_charge = max_speed_truck
                # Calculamos la carga efectiva
                if(inductive):
                    charge_power_isleta = charge_power_isleta*0.7
                if(charge_power_isleta < max_speed_truck):
                    effective_charge = charge_power_isleta

                total_power_supplied += truck.charge(effective_charge, t_increment)
                if(truck.is_full()):
                    trucks_isleta_new = trucks_isleta.remove(truck)
            trucks_isleta = trucks_isleta_new

        
        # Rellenar isletas vacías
        for isleta in isletas:
            #Comprobar si se han cargado todos los camiones
            if(len(trucks_ordered)==0):
                finished=True
                break
            if(isleta.get_free_spaces() == 0):
                continue
            if(check_truck_isleta(trucks_ordered[0], isleta)):
                isleta.occupy(trucks_ordered[0])
                trucks_ordered.pop(0)
                continue
        t += t_increment
        

    print(f"Tiempo: {t*t_multiplier} h, Potencia total suministrada: {total_power_supplied*t_multiplier} kW")
        


if __name__ == "__main__":
    main()

