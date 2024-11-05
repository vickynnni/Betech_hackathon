import random
from matplotlib import pyplot as plt
from typing import List, Tuple

class Truck:
    '''
        Clase que modela un camion
    '''
    def __init__(self, battery_capacity : float, charging_ports : List[str], charging_speed : float):
        self.battery_capacity = battery_capacity # En kW h
        self.current_battery = 0                 # Carga actual (empieza a 0 siempre!)
        self.charging_ports = charging_ports     # Listado de puntos de carga, por ejemplo ['top', 'right']
        self.charging_speed = charging_speed     # Límite de velocidad de carga en kW

    def __str__(self):
        return f"Truck: Battery Capacity - {self.battery_capacity}, Charging Ports - {', '.join(self.charging_ports)}, Charging Speed - {self.charging_speed}"
    
    def is_full(self) -> bool:
        '''
            Retorna si la bateria esta llena
        '''
        if(self.current_battery >= self.battery_capacity):
            #print(f"Truck full. Battery capacity: {self.battery_capacity} Total charge: {self.current_battery}")
            return True
        return False

    def add_charge(self, charge_power : float) -> None:
        '''
            Carga la bateria si y solo si es menor a 100
        '''
        if self.current_battery < 100.0:
            self.current_battery += charge_power 
        else:
            self.current_battery = 100.0

    def get_charge(self, charge_power : float, time_increment : int, t_multiplier : float) -> float:
        '''
            Retorna cuanto se va a cargar la bateria en el instante de tiempo 'time_increment'.
            't_multiplier' es el factor de conversion del tiempo a horas
        '''
        power_supplied : float = charge_power*time_increment*t_multiplier
        #self.current_battery += power_supplied
        return power_supplied

class GrupoIsleta:
    '''
        Clase que modela un grupo de isletas
    '''
    def __init__(self, n_isletas : int, charge_power : float, charging_ports : List[str]):
        self.charge_power = charge_power # Capacidad de carga de la isleta (en kW)
        self.charging_ports = charging_ports # Puertos de carga que admite la isleta
        self.trucks = [] # Camiones en la isleta (len(trucks) == n_isletas)
        self.n_isletas = n_isletas
        self.is_clean = False # Nos dice si la isleta sólo se carga con energía limpia o no

    def __str__(self):
        return f"Isleta: Charge Power - {self.charge_power}, Charging Ports - {', '.join(self.charging_ports)}, Trucks - {len(self.trucks)}, Free Spaces - {self.get_free_spaces()}"
    
    def get_free_spaces(self) -> int:
        '''
            Devuelve el numero de isletas libres en el grupo
        '''
        return self.n_isletas-len(self.trucks)
    
    def occupy(self,truck: Truck) -> bool:
        '''
            Anade un camion al grupo. 
            Devuelve True si se ha podido, False en caso contrario
        '''
        if(len(self.trucks) < self.n_isletas):
            self.trucks.append(truck)
            return True
        return False
    
    def get_trucks(self) -> List[Truck]:
        '''
            Devuelve los camiones en el grupo de isletas
        '''
        return self.trucks
    
    def set_trucks(self,trucks):
        self.trucks = trucks

####################################################################################################################################
####################################################################################################################################
####################################################################################################################################

def get_trucks(n : int) -> List[Truck]:
    '''
        Crea y devuelve una lista de 'n' camiones con valores aleatorios
    '''
    #random.seed(2231)
    trucks : List[Truck] = []

    for _ in range(n):
        # Generar valores aleatorios
        battery_capacity = random.randint(100, 500)  # Capacidad de 100 a 500 kWh
        charging_ports = random.sample(['top', 'right', 'left', 'inductive'], k=random.randint(1, 4))  # 1 a 4 puertos de carga
        charging_speed = random.randint(20, 250)  # Velocidad de carga entre 50 y 200 kW

        # Crear y agregar el camión a la lista
        truck = Truck(battery_capacity, charging_ports, charging_speed)
        trucks.append(truck)

    return trucks

def check_truck_isleta(truck: Truck, isleta: GrupoIsleta) -> bool:
    '''
        Comprueba si un camion se puede dockear a una isleta (si y solo si coincide su puerto de carga)
    '''
    for port in truck.charging_ports:
        if port in isleta.charging_ports:
            return True
    return False

def check_inductiva(truck: Truck, isleta: GrupoIsleta) -> bool:
    '''
        Devuelve si el unico puerto de carga comun es inductivo
    '''
    intersection = set(truck.charging_ports).intersection(set(isleta.charging_ports))
    if(len(intersection))==1 and 'inductive' in intersection:
        return True
    return False

def check_no_truck_isleta(isletas : List[GrupoIsleta]) -> bool:
    '''
        Devuelve True si todas las isletas estan vacías
    '''
    for isleta in isletas:
        if(isleta.get_free_spaces() < isleta.n_isletas):
            return False
    return True

def plot_trucks_time(ts : List[float], trucks_t : List[int]) -> None:
    '''
        Plotea horas transcurridas vs n° de camiones cargados
    '''
    # Plot data
    plt.subplot(1, 2, 1)  # (rows, columns, index)
    plt.plot(ts, trucks_t)
    plt.xlabel('Time (h)')
    plt.ylabel('Trucks charged')
    plt.title('Trucks charged over time')

def plot_kw_time(ts : List[float], kw_t : List[float]):
    '''
        Plotea horas transcurridas vs energia suministrada
    '''
    
    # Plot data
    plt.subplot(1, 2, 2)  # (rows, columns, index)
    plt.plot(ts, kw_t)
    plt.xlabel('Time (h)')
    plt.ylabel('Power supplied (kW)')
    plt.title('Power supplied over time')


def efficiency_score(truck: Truck, isleta: GrupoIsleta):
    '''
        Por cada isleta, les asigna un score a cada truck que indica que tan 'probable' es que se le asigne esa isleta para cargarlo 
    '''
    # Valor de penalizacion
    penalization = 1
    
    # Los camiones que no pueden cargar en la isleta tienen un score de 0
    if(not check_truck_isleta(truck, isleta)):
        return 0
    
    # Capacidad de carga se vera afecta si el puerto carga por inductividad
    inductiva = 0.7 if check_inductiva(truck, isleta) else 1
    
    # Cociente entre la velocidad de carga y la capacidad de carga de la isleta 
    ratio_truck_isleta = truck.charging_speed/(isleta.charge_power*inductiva)
    
    # Si la velocidad de carga es mayor a la capacidad de carga de la isleta, el camion no se esta cargando todo lo rapido que podria
    if(ratio_truck_isleta > 1):
        penalization *= 0.8

    # El camion y la isleta comparten velocidad de carga y capacidad de carga
    elif(ratio_truck_isleta == 1):
        ratio_truck_isleta = 0.99

    # Si la velocidad de carga es menor a la capacidad de carga de la isleta, el camion esta desaprovechando la isleta 
    elif(ratio_truck_isleta < 0.4): #Penalizamos trucks que no se cargan lo suficiente respecto a la isleta
        penalization *= 0.8

    # Tiempo que tarda en cargar el camion
    charging_time : float = truck.battery_capacity/truck.charging_speed
    
    # Score final
    score = abs(charging_time / (1-ratio_truck_isleta)) * penalization
    return score

def fill_isletas(isletas, trucks, current_clean_energy):
    for isleta in isletas:
        if(check_isleta_clean(isleta, current_clean_energy)):
            continue # Pasamos de la isleta limpia si no tenemos energía limpia
        i = 0
        
        # Ordenamos los camiones por su efficiency score
        trucks_ordered = sorted(trucks, key=lambda x: efficiency_score(x,isleta), reverse=True)
        
        # Se iteran por todas las isletas libres en el grupo, anadiendo todos los que sean compatibles en orden descendente de efficiency score
        while(isleta.get_free_spaces() != 0):
            if(i>=len(trucks_ordered)):
                    break
            if(check_truck_isleta(trucks_ordered[i],isleta)):
                isleta.occupy(trucks_ordered[i])
                trucks.remove(trucks_ordered[i])
                i += 1
                continue
            else:
                i += 1
                continue
            
    return isletas, trucks


def check_isleta_clean(isleta, remaining_clean_energy):
    if(isleta.is_clean):
        if(remaining_clean_energy <= 0):
            return True
    return False

def run_simulation(isletas,trucks=[]):
    if(len(trucks) == 0):
        trucks = get_trucks(100)
    
    # Variables para unidades de tiempo
    
    # Tiempo (s)
    t : float = 0
    
    # # Para pasar de segundos a la unidad de tiempo escogida
    t_multiplier : float = 1/60

    # Incremento de tiempo en segundos
    t_increment : int = 1
    
    # Proceso principal
    finished=False

    # Variable para contar cuánta energía limpia nos queda (kWh)
    total_clean_energy = 500
    current_clean_energy = total_clean_energy
    # Variable para contar la energía que acaban recibiendo los camiones. 
    # Debería ser igual a la suma de las capacidades de los camiones
    total_power_supplied_to_trucks : float = 0 
    
    # Variable para contar la energía que se suministra desde las isletas
    total_power_supplied : float= 0
    
    # Suma de las capacidades de los camiones
    total_charging_power : float = 0
    for truck in trucks:
        total_charging_power += truck.battery_capacity

    #Rellenar isletas vacías (inicial)
    [isletas,trucks] = fill_isletas(isletas, trucks,current_clean_energy)
    charged_trucks = 0

    # Variables para plotear
    ts = []
    trucks_t = []
    kw_t = []

    # Bucle principal
    clean_emptied = False
    while(True):
        ts.append(t)
        #Cargar los camiones
        
        for isleta in isletas:

            trucks_isleta = isleta.get_trucks()
            if(check_isleta_clean(isleta, current_clean_energy)):
                continue # Pasamos de la isleta limpia si no tenemos energía limpia
            
            for truck in trucks_isleta:
                if(not clean_emptied):
                    use_clean = True # En principio usamos energía limpia
                else:
                    use_clean = False
                max_speed_truck = truck.charging_speed
                charge_power_isleta = isleta.charge_power
                inductive = check_inductiva(truck, isleta)
                effective_charge = max_speed_truck
                total_power_supplied += truck.get_charge(effective_charge, t_increment, t_multiplier)
                # Calculamos la carga efectiva
                if(inductive):
                    charge_power_isleta = charge_power_isleta*0.7
                    use_clean = False
                effective_charge = min(charge_power_isleta, max_speed_truck)

                truck_charge = truck.get_charge(effective_charge, t_increment, t_multiplier)

                if(use_clean):
                    if(current_clean_energy >= truck_charge):
                        current_clean_energy -= truck_charge
                    else:
                        truck_charge = current_clean_energy
                        current_clean_energy = 0
                        clean_emptied = True

                truck.add_charge(truck_charge)
                total_power_supplied_to_trucks += truck_charge
                if(truck.is_full()):
                    charged_trucks += 1
                    trucks_isleta.remove(truck)
                
                elif(clean_emptied):
                    for clean_trucks in trucks_isleta:
                        trucks.append(clean_trucks) # Devolvemos el camión a la lista de camiones porque no ha terminado de cargar
                    trucks_isleta = []
                    break

            isleta.set_trucks(trucks_isleta)
    
        trucks_t.append(charged_trucks)
        kw_t.append(total_power_supplied)

        #Rellenar isletas vacías por si se ha liberado algún espacio
        [isletas,trucks] = fill_isletas(isletas, trucks,current_clean_energy)

        if(len(trucks) == 0):
            finished = True
                    
        # Stop condition
        if(finished and check_no_truck_isleta(isletas)):
            break
        t += t_increment
        
    clean_energy_used = total_clean_energy - current_clean_energy
    #total_power_supplied -= clean_energy_used
    perdida_energia = 100*(1-total_power_supplied_to_trucks/total_power_supplied)
    total_g_CO2 = (total_power_supplied - clean_energy_used)*450
    # print(f"Total charging power: {total_charging_power} kWh")
    # print(f"Camiones cargados: {charged_trucks}, Tiempo: {t*t_multiplier} h, Potencia total suministrada desde isletas: {total_power_supplied} kW, Potencia total suministrada a camiones: {total_power_supplied_to_trucks} kW")
    # print(f"% Pérdida de energía: {100*(1-total_power_supplied_to_trucks/total_power_supplied)}")
    # plot_trucks_time(ts, trucks_t)
    # plot_kw_time(ts, kw_t)
    # plt.tight_layout()
    # plt.show()
    return total_charging_power, charged_trucks, t*t_multiplier, total_power_supplied, perdida_energia, total_g_CO2

def print_results(mean_charging_power, mean_charged_trucks, mean_time, mean_perdida_energia, mean_power_supplied, mean_g_CO2):
    '''
        Prints results as specified in the enunciado
    '''
    print()
    print(f"Total charging power: {mean_charging_power} kWh\n")
    
    print("#####################")
    print(f"Camiones cargados: {mean_charged_trucks} camiones \n")
          
    print("#####################")
    print(f"Tiempo: {mean_time} h\n")
    
    print("#####################")
    print(f"kW consumidos: {mean_power_supplied} kW\n")
    
    print("#####################")
    print(f"% Pérdida de energía: {mean_perdida_energia}\n")

    print("#####################")
    print(f"CO2 emitido: {mean_g_CO2/1000} Kg\n")



def main():
    # Construir estructuras
    isletas = []
    isletas.append(GrupoIsleta(5, 250, ['right', 'left', 'top'], True))
    isletas.append(GrupoIsleta(7, 150, ['right', 'top']))
    isletas.append(GrupoIsleta(3, 110, ['top', 'inductive']))
    isletas.append(GrupoIsleta(5, 60, ['left','top','inductive']))

    mean_charging_power = 0
    mean_charged_trucks = 0
    mean_time = 0
    mean_power_supplied = 0
    mean_perdida_energia = 0
    mean_g_CO2 = 0
    n = 1
    for i in range(n):
        print('.', end='', flush=True)
        [total_charging_power, charged_trucks, time, total_power_supplied, perdida_energia, total_g_CO2] = run_simulation(isletas)
        mean_charging_power += total_charging_power
        mean_charged_trucks += charged_trucks
        mean_time += time
        mean_power_supplied += total_power_supplied
        mean_perdida_energia += perdida_energia
        mean_g_CO2 += total_g_CO2
    
    mean_charging_power /= n
    mean_charged_trucks /= n
    mean_time /= n
    mean_power_supplied /= n
    mean_perdida_energia /= n
    mean_g_CO2 /= n

    print_results(mean_charging_power=mean_charging_power, mean_charged_trucks=mean_charged_trucks, mean_time=mean_time, mean_perdida_energia=mean_perdida_energia , mean_power_supplied=mean_power_supplied, mean_g_CO2=mean_g_CO2)


if __name__ == "__main__":
    main()

