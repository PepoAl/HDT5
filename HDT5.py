import simpy
import random
import statistics

RANDOM_SEED = 42
RAM_CAPACITY = 100
CPU_SPEED = 3
INTERVAL = 10
NUM_PROCESSES = 25

tiempos_netos = []

def proceso(env, nombre, ram, cpu):
    tiempo_inicio = env.now
    print(f"{nombre} llega al sistema en el tiempo {tiempo_inicio}")
    memoria_necesaria = random.randint(1, 10)

    with ram.get(memoria_necesaria) as req:
        yield req
        print(f"{nombre} obtiene {memoria_necesaria} de memoria RAM en el tiempo {env.now}")
        instrucciones_restantes = random.randint(1, 10)

        while instrucciones_restantes > 0:
            with cpu.request() as req_cpu:
                yield req_cpu
                print(f"{nombre} empieza a ejecutar en el CPU en el tiempo {env.now}")
                yield env.timeout(CPU_SPEED)
                instrucciones_ejecutadas = min(instrucciones_restantes, CPU_SPEED)
                instrucciones_restantes -= instrucciones_ejecutadas
                print(f"{nombre} ejecuta {instrucciones_ejecutadas} instrucciones en el CPU")

                if instrucciones_restantes == 0:
                    tiempo_fin = env.now
                    tiempo_neto = tiempo_fin - tiempo_inicio
                    tiempos_netos.append(tiempo_neto)
                    print(f"{nombre} ha terminado en el tiempo {tiempo_fin}, tiempo neto: {tiempo_neto}")

        ram.put(memoria_necesaria)
        print(f"{nombre} devuelve {memoria_necesaria} de memoria RAM en el tiempo {env.now}")

def llegada_proceso(env, ram, cpu):
    for i in range(NUM_PROCESSES):
        env.process(proceso(env, f'Proceso-{i}', ram, cpu))
        yield env.timeout(random.expovariate(1.0 / INTERVAL))

env = simpy.Environment()
random.seed(RANDOM_SEED)

RAM = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)
CPU = simpy.Resource(env, capacity=1)

env.process(llegada_proceso(env, RAM, CPU))
env.run()

tiempo_promedio = sum(tiempos_netos) / len(tiempos_netos)
desviacion_estandar = statistics.stdev(tiempos_netos)

print(f"Tiempo promedio de ejecución: {tiempo_promedio}")
print(f"Desviación estándar: {desviacion_estandar}")
