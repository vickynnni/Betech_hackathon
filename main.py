import random
from matplotlib import pyplot as plt

class Truck:
    def __init__(self, battery_capacity, charging_ports, charging_speed):
        self.battery_capacity = battery_capacity
        self.current_battery = 0
        self.charging_ports = charging_ports  # Listado de puntos de carga, por ejemplo ['top', 'right']
        self.charging_speed = charging_speed  # Límite de velocidad de carga en kW

    def __str__(self):
        return f"Truck: Battery Capacity - {self.battery_capacity}, Charging Ports - {', '.join(self.charging_ports)}, Charging Speed - {self.charging_speed}"
    
    def is_full(self):
        if(self.current_battery >= self.battery_capacity):
            #print(f"Truck full. Battery capacity: {self.battery_capacity} Total charge: {self.current_battery}")
            return True
        return False

    def add_charge(self, charge_power):
        self.current_battery += charge_power

    def get_charge(self, charge_power, time_increment, t_multiplier):
        power_supplied = charge_power*time_increment*t_multiplier
        #self.current_battery += power_supplied
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
    #random.seed(2231)
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

def check_no_truck_isleta(isletas):
    for isleta in isletas:
        if(isleta.get_free_spaces() < isleta.n_isletas):
            return False
    return True

def plot_trucks_time(ts, trucks_t):
    # Plot data
    plt.subplot(1, 2, 1)  # (rows, columns, index)
    plt.plot(ts, trucks_t)
    plt.xlabel('Time (m)')
    plt.ylabel('Trucks charged')
    plt.title('Trucks charged over time')

def plot_kw_time(ts, kw_t):
    # Plot data
    plt.subplot(1, 2, 2)  # (rows, columns, index)
    plt.plot(ts, kw_t)
    plt.xlabel('Time (m)')
    plt.ylabel('Power supplied (kW)')
    plt.title('Power supplied over time')
    


def efficiency_score(truck: Truck, isleta: GrupoIsleta):
    fits = 1
    penalization = 1
    if(not check_truck_isleta(truck, isleta)): # Los camiones que no pueden cargar en la isleta tienen un score de 0
        fits = 0
    inductiva = 0.7 if check_inductiva(truck, isleta) else 1
    ratio_truck_isleta = truck.charging_speed/(isleta.charge_power*inductiva)
    #print(f"Ratio truck isleta: {ratio_truck_isleta}")
    if(ratio_truck_isleta > 1):
        penalization *= 0.8
    if(ratio_truck_isleta == 1):
        ratio_truck_isleta = 0.99 #Evitamos divisiones por 0
    if(ratio_truck_isleta < 0.4): #Penalizamos trucks que no se cargan lo suficiente respecto a la isleta
        penalization *= 0.8
    score = abs((truck.battery_capacity/(truck.charging_speed)) / (1-ratio_truck_isleta)) * fits * penalization
    return score

def fill_isletas(isletas, trucks):
    for isleta in isletas:
        i = 0
        trucks_ordered = sorted(trucks, key=lambda x: efficiency_score(x,isleta), reverse=True)
        while(isleta.get_free_spaces() != 0):
            if(i>=len(trucks_ordered)):
                    break
            if(check_truck_isleta(trucks_ordered[i],isleta)):
                isleta.occupy(trucks_ordered[i])
                #print(f"Truck {i} added to isleta")
                trucks.remove(trucks_ordered[i])
                i += 1
                continue
            else:
                i += 1
                continue
    return isletas, trucks

def run_simulation(isletas):
    trucks = get_trucks(100)
    
    # Variables para unidades de tiempo
    t=0 # Tiempo s
    t_multiplier = 1/60 # Para pasar de segundos a horas
    t_increment = 1 # Incremento de tiempo en segundos
    # Proceso principal
    finished=False
    #Ordenar por menor capacidad de batería
   
    # Variable para contar la energía que acaban recibiendo los camiones. 
    # Debería ser igual a la suma de las capacidades de los camiones
    total_power_supplied_to_trucks = 0 
    # Variable para contar la energía que se suministra desde las isletas
    total_power_supplied = 0
    
    # Suma de las capacidades de los camiones
    total_charging_power = 0
    for truck in trucks:
        total_charging_power += truck.battery_capacity

    #Rellenar isletas vacías (inicial)
    [isletas,trucks] = fill_isletas(isletas, trucks)
    charged_trucks = 0

    # For plotting data
    ts = []
    trucks_t = []
    kw_t = []

    # Bucle principal
    while(True):
        ts.append(t)
        #Cargar los camiones
        for isleta in isletas:
            trucks_isleta = isleta.get_trucks()
            trucks_isleta_new = []
            for truck in trucks_isleta:
                max_speed_truck = truck.charging_speed
                charge_power_isleta = isleta.charge_power
                inductive = check_inductiva(truck, isleta)
                effective_charge = max_speed_truck

                total_power_supplied += truck.get_charge(effective_charge, t_increment, t_multiplier)
                # Calculamos la carga efectiva
                if(inductive):
                    charge_power_isleta = charge_power_isleta*0.7
                effective_charge = min(charge_power_isleta, max_speed_truck)

                truck_charge = truck.get_charge(effective_charge, t_increment, t_multiplier)
                truck.add_charge(truck_charge)
                total_power_supplied_to_trucks += truck_charge
                if(truck.is_full()):
                    charged_trucks += 1
                    trucks_isleta_new = trucks_isleta.remove(truck)
            trucks_isleta = trucks_isleta_new

        trucks_t.append(charged_trucks)
        kw_t.append(total_power_supplied)
        #Rellenar isletas vacías por si se ha liberado algún espacio
        [isletas,trucks] = fill_isletas(isletas, trucks)

        if(len(trucks) == 0):
            finished = True
                    
        # Stop condition
        if(finished and check_no_truck_isleta(isletas)):
            break
        t += t_increment
        
    
    perdida_energia = 100*(1-total_power_supplied_to_trucks/total_power_supplied)
    # print(f"Total charging power: {total_charging_power} kWh")
    # print(f"Camiones cargados: {charged_trucks}, Tiempo: {t*t_multiplier} h, Potencia total suministrada desde isletas: {total_power_supplied} kW, Potencia total suministrada a camiones: {total_power_supplied_to_trucks} kW")
    # print(f"% Pérdida de energía: {100*(1-total_power_supplied_to_trucks/total_power_supplied)}")
    # plot_trucks_time(ts, trucks_t)
    # plot_kw_time(ts, kw_t)
    # plt.tight_layout()
    # plt.show()
    return total_charging_power, charged_trucks, t*t_multiplier, total_power_supplied, perdida_energia

def main():
    # Construir estructuras
    isletas = []
    isletas.append(GrupoIsleta(5, 250, ['right', 'left', 'top']))
    isletas.append(GrupoIsleta(7, 150, ['right', 'top']))
    isletas.append(GrupoIsleta(3, 110, ['top', 'inductive']))
    isletas.append(GrupoIsleta(5, 60, ['left','top','inductive']))

    mean_charging_power = 0
    mean_charged_trucks = 0
    mean_time = 0
    mean_power_supplied = 0
    mean_perdida_energia = 0
    n = 30
    for i in range(n):
        print('.', end='', flush=True)
        [total_charging_power, charged_trucks, time, total_power_supplied, perdida_energia] = run_simulation(isletas)
        mean_charging_power += total_charging_power
        mean_charged_trucks += charged_trucks
        mean_time += time
        mean_power_supplied += total_power_supplied
        mean_perdida_energia += perdida_energia
    mean_charging_power /= n
    mean_charged_trucks /= n
    mean_time /= n
    mean_power_supplied /= n
    mean_perdida_energia /= n
    print()
    print(f"Total charging power: {mean_charging_power} kWh")
    print(f"Camiones cargados: {mean_charged_trucks}, Tiempo: {mean_time} h, Potencia total suministrada desde isletas: {mean_power_supplied} kW")
    print(f"% Pérdida de energía: {mean_perdida_energia}")


if __name__ == "__main__":
    main()

