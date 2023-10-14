from math import log
import numpy as np
from Systems import QueueingSystem
from Demand import Demand

class QueueingNetwork:

    def __init__(self, t_max:int, L:int, lambda_0:float, theta:np.ndarray, mu:tuple, gamma:tuple) -> None:
        self.t_max = t_max
        self.L = L
        self.lambda_0 = lambda_0
        self.theta = theta
        self.mu = mu
        self.gamma = gamma
        
        self.t_now = 0
        self.t_old = 0
        self.indicator = False

        # моменты активации процессов 
        # обслуживания (_ = 1, L + 1)
        # генерации (_ = 0)
        self.t_processes = [t_max + 1 for _ in range(L + 1)]
        self.t_processes[0] = 0
        self.init_systems()

    def init_systems(self):
        systems = [QueueingSystem(0, 0, 0, 0)] # источник
        systems[0].serialization([0])
        for system in range(1, self.L + 1):
            systems.append(QueueingSystem(system, 1, self.mu[system - 1], self.gamma[system - 1]))          
            systems[-1].serialization([0])
        self.systems = tuple(systems)

    def arrival_time(self):
        return -log(np.random.random()) / self.lambda_0
    
    def routing(self, i:int, demand:Demand):
        r = np.random.random()
        tmp_sum = 0
        j = 0
        while True:
            if self.theta[i][j] > 0:
                tmp_sum += self.theta[i][j]
            if tmp_sum >= r:
                break
            j += 1
        print(f'\tтребование {demand.id} переходит из {i} в {j}')
        
        i_states = self.systems[i].deserialization()
        j_states = self.systems[j].deserialization()

        if i == 0:
            self.systems[j].update_time_states(self.t_now, 1)
            self.systems[j].demands.append(demand)
        # если требование выходит из сети
        elif j == 0:
            self.systems[i].update_time_states(self.t_now, -1)
            self.systems[i].demands.remove(demand)
            print(f'\tтребование {demand.id} покинуло сеть')
        else:
            self.systems[i].update_time_states(self.t_now, -1)
            self.systems[i].demands.remove(demand)
            self.systems[j].update_time_states(self.t_now, 1)
            self.systems[j].demands.append(demand)

        self.systems[i].serialization(i_states)
        self.systems[j].serialization(j_states)
        print(f'\tтребования в {i}: {self.systems[i].current_demands()}')
        print(f'\tтребования в {j}: {self.systems[j].current_demands()}')

    def simulation(self):
        demand_id = 0
        while self.t_now < self.t_max:
            print(f'{self.t_now}:')
            # [print(f'{system.id}\n\t{system.time_states}\n\t{len(system.demands)}') for system in self.systems]
            self.indicator = False

            # генерация требования
            if (self.t_processes[0] == self.t_now):
                self.indicator = True
                self.t_processes[0] = self.t_now + self.arrival_time()
                demand_id += 1
                demand = Demand(demand_id, self.t_now)
                print(f'\tтребование {demand_id} поступило в сеть')
                self.routing(0, demand)

            for i in range(1, self.L + 1):
                # начало обслуживания
                if self.systems[i].service_flag == False and len(self.systems[i].demands) > 0:
                    self.indicator = True
                    self.systems[i].service_flag = True
                    self.t_processes[i] = self.t_now + self.systems[i].service_time()
                    print(f'\tтребование \
{self.systems[i].demands[0].id} \
начало обслуживаться в системе \
{self.systems[i].id}')

                # завершение обслуживания
                if self.t_processes[i] == self.t_now:
                    self.indicator = True
                    self.systems[i].service_flag = False
                    print(f'\tтребование \
{self.systems[i].demands[0].id} \
закончило обслуживаться в системе \
{self.systems[i].id}')
                    self.routing(i, self.systems[i].demands[0])
                    self.t_processes[i] = self.t_max + 1
            
            if not self.indicator:
                for system in self.systems:
                    system.continue_time_states(self.t_now, self.t_old)
                # статистика
                print('------')
                for i in range(self.L + 1):
                    print(f'Система {i}:\n{[state / self.t_max for state in self.systems[i].deserialization()]}')
                    print(sum(self.systems[i].deserialization()), self.t_max)
                print('------\n')
                self.t_old = self.t_now
                self.t_now = min(self.t_processes)

                

        print()
        for i in range(self.L + 1):
            print(f'Система {i}:\n{[state / self.t_max for state in self.systems[i].deserialization()]}')
            print(sum(self.systems[i].deserialization()), self.t_max)
        print()



