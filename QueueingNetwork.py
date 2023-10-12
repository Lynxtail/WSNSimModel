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
        self.indicator = False

        # моменты активации процессов 
        # обслуживания (_ = 1, L + 1)
        # генерации (_ = 0)
        self.t_processes = [t_max + 1 for _ in range(L + 1)]

    def init_systems(self):
        systems = list()
        for system in range(self.L):
            systems.append(QueueingSystem(system + 1, 1, self.mu[system], self.gamma[system]))          
            systems[-1].serialization()
        self.systems = tuple(systems)

    def arrival_time(self):
        return -log(np.random.random()) / self.lambda_0
    
    def routing(self, i:int, demand_id:int):
        r = np.random.random()
        tmp_sum = 0
        j = -1
        while tmp_sum < r:
            j += 1
            if self.theta[i][j] > 0:
                tmp_sum += self.theta[i][j]
        # если требование выходит из сети
        if j == 0:
            pass
        else:
            self.systems[i].time_states[len(self.systems[i].demands)] += self.t_now - max(self.systems[i].deserialization())
            if i != 0:
                self.systems[i].demands.remove(demand_id)
            self.systems[j].demands.append(demand_id)

    def simulation(self):
        id = 0
        while self.t_now < self.t_max:
            self.indicator = False

            # генерация требования
            if (self.t_processes[0] == self.t_now):
                self.indicator = True
                self.t_processes[0] = self.arrival_time()
                demand = Demand(id + 1, self.t_now)
                self.routing(0, demand.id)

            for i in range(1, self.L + 1):
                # начало обслуживания
                if self.systems[i].service_flag == False and len(self.systems[i].demands) > 0:
                    self.indicator(True)
                    self.systems[i].service_flag = True
                    self.t_processes[i] = self.t_now + self.systems[i].service_time()

                # завершение обслуживания
                if self.t_processes[i] == self.t_now:
                    self.indicator(True)
                    self.systems[i].service_flag = False
                    self.routing(i, self.systems[i].demands[0].id)
                    self.t_processes[i] = self.t_max + 1
            
            if not self.indicator:
                # статистика
                for system in self.systems:
                    system.time_states += system.deserialization()
                    system.serialization()
                    system.time_states = list()
                self.t_now = min(self.t_processes)




