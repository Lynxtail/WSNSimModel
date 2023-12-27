from math import log
import numpy as np
from Systems import QueueingSystem
from Demand import Demand

class QueueingNetwork:

    def __init__(self, t_max:int, L:int, lambda_0:float, theta:np.ndarray, mu:tuple, gamma:tuple, tau_threshold:float) -> None:
        self.t_max = t_max
        self.L = L
        self.lambda_0 = lambda_0
        self.theta = theta
        self.initial_theta = theta
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

        self.serviced_demands = 0
        self.lost_demands = 0
        self.total_demands = 0
        self.sum_life_time = 0
        self.b = [1] * L
        self.count_states = 1
        self.tau_summarized = 0

        self.tau = 0
        self.tau_threshold = tau_threshold

    def init_systems(self):
        systems = [QueueingSystem(0, 0, 0, 0)] # источник
        systems[0].serialization_time_states([0])
        for system in range(1, self.L + 1):
            systems.append(QueueingSystem(system, 1, self.mu[system - 1], self.gamma[system - 1]))          
            systems[-1].serialization_time_states([0])
            systems[-1].be_destroyed_at = self.t_now + systems[-1].destroy_time()
            # print(systems[-1].be_destroyed_at)
        self.systems = tuple(systems)

    def arrival_time(self):
        return -log(np.random.random()) / self.lambda_0
    
    def change_theta(self) -> np.ndarray:
        old_theta = np.copy(self.theta)
        new_theta = np.copy(old_theta)
        for m, item in enumerate(self.b):
            if item == 0:
                for i in range(self.L + 1):
                    for k in range(self.L + 1):
                        if i != m + 1 and k != m + 1:
                            if old_theta[i][m + 1] != 1:
                                new_theta[i][k] = old_theta[i][k] / (1 - old_theta[i][m + 1])
                        elif k != m + 1:
                            new_theta[m + 1][k] = 0
                        elif i != m + 1:
                            new_theta[i][m + 1] = 0
                new_theta[m + 1][m + 1] = 1
            old_theta = np.copy(new_theta)
        return new_theta

    def check_matrix(self) -> bool:
        excepted = []
        for i in range(len(self.theta)):
            if self.theta[i][i] == 1: excepted.append(i)

        def dfs(start):
            for ind, v in enumerate(self.theta[start] > 0):
                if v:
                    visited[start] = True
                    if not visited[ind]:
                        # print(ind, end=' ')
                        dfs(ind)

        # flag = True
        visited = []
        for i in range(self.L + 1):
            if not i in excepted:
                visited = [False] * (self.L + 1)
                for m in excepted:
                    visited[m] = True
                if not visited[i]:
                    # print(f'\n\tдля {i}:', end=' ')
                    dfs(i)
                    # print()
                    if not all(visited): return False
        return all(visited) if visited else False

    def routing(self, i:int, demand:Demand):
        r = np.random.random()
        tmp_sum = 0
        j = 0
        while j < self.L:
            if self.theta[i][j] > 0:
                tmp_sum += self.theta[i][j]
            if tmp_sum >= r:
                break
            j += 1
        # print(f'\tтребование {demand.id} переходит из {i} в {j}')

        if i != 0:
            self.systems[i].update_time_states(self.t_now)
            self.systems[i].demands.remove(demand)
            # print(f'\tтребования в {i}: {self.systems[i].current_demands()}')
        if j != 0:
            self.systems[j].update_time_states(self.t_now)
            self.systems[j].demands.append(demand)
            # print(f'\tтребования в {j}: {self.systems[j].current_demands()}')
        else:
            self.serviced_demands += 1
            self.sum_life_time += self.t_now - demand.arrival
    
    def restore(self):
        print(f'Сеть восстанавливается при\nb: {self.b}')
        self.b = [1] * self.L
        self.theta = np.copy(self.initial_theta)
        for system in self.systems[1:]:
            # print(system.gamma)
            system.be_destroyed_at = self.t_now + system.destroy_time()

    def simulation(self):
        demand_id = 0
        while self.t_now < self.t_max:
            print(f'{self.t_now}')
            [print(f'{system.id}\n\t{system.deserialization_time_states()}\n\t{len(system.demands)}') for system in self.systems]
            self.indicator = False

            # генерация требования
            if (self.t_processes[0] == self.t_now):
                self.indicator = True
                self.t_processes[0] = self.t_now + self.arrival_time()
                demand_id += 1
                demand = Demand(demand_id, self.t_now)
                self.total_demands += 1
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
                    self.tau = self.sum_life_time / self.serviced_demands if self.serviced_demands != 0 else 0
                    self.t_processes[i] = self.t_max + 1

                # выход из строя
                if self.systems[i].be_destroyed_at == self.t_now:
                    print(f'Система {i} выходит из строя')
                    self.systems[i].state = False
                    self.lost_demands += len(self.systems[i].demands)
                    print(self.systems[i].current_demands())
                    self.systems[i].demands.clear()
                    self.b[i - 1] = 0
                    self.systems[i].be_destroyed_at = self.t_max + 1
                    self.t_processes[i] = self.t_max + 1
                    self.theta = self.change_theta()
                    if not self.check_matrix():
                        self.restore()
                    self.tau_summarized += self.sum_life_time / self.serviced_demands if self.serviced_demands != 0 else 0
                    self.count_states += 1
                    self.serviced_demands = 0
                    self.sum_life_time = 0

            if self.tau > self.tau_threshold:
                self.restore()
                self.tau_summarized += self.sum_life_time / self.serviced_demands if self.serviced_demands != 0 else 0
                self.count_states += 1
                self.serviced_demands = 0
                self.sum_life_time = 0


            if not self.indicator:
                # статистика
                for system in self.systems:
                    system.update_time_states(self.t_now)
                
                print('------')
                print(f'tau for {self.b} = {self.tau}')
                for i in range(self.L + 1):
                    print(f'Система {i}:\n{[state / self.t_max for state in self.systems[i].deserialization_time_states()]}')
                print('------\n')

                self.t_old = self.t_now
                self.t_now = min(self.t_processes + [system.be_destroyed_at for system in self.systems[1:]])

        print(f'\nВсего требований: {self.total_demands}\nОбслужено {self.total_demands - self.lost_demands}, потеряно {self.lost_demands}')
        print(f'tau = {self.tau_summarized / self.count_states if self.tau_summarized != 0 else self.tau}')
        print(f'p_lost = {self.lost_demands / self.total_demands}')
        print("p:")
        for i in range(self.L + 1):
            print(f'\tСистема {i}:{sum([state / self.t_max for state in self.systems[i].deserialization_time_states()])}')
            print(f'\tСистема {i}:\n\t{[state / self.t_max for state in self.systems[i].deserialization_time_states()]}\n')



