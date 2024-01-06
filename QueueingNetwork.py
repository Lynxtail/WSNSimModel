from math import log
import numpy as np
import os
import gc
from Systems import QueueingSystem


class QueueingNetwork:

    def __init__(self, t_max:int, L:int, lambda_0:float, theta:np.ndarray, mu:tuple, gamma:tuple, tau_threshold:float) -> None:
        self.t_max = t_max
        self.L = L
        self.lambda_0 = lambda_0
        self.theta = theta
        self.initial_theta = theta
        self.mu = mu
        self.gamma = gamma

        # self.systems = tuple()
        
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
        for item in os.listdir():
            if "system" in item:
                os.remove(item)
        QueueingSystem(system_id=0, server_cnt=0, mu=0, gamma=0, time_states=[0]).save() # источник
        for i in range(1, self.L + 1):
            system = QueueingSystem(system_id=i, server_cnt=1, mu=self.mu[i - 1], gamma=self.gamma[i - 1], time_states=[0])
            system.be_destroyed_at = self.t_now + system.destroy_time()
            system.save()
        # self.systems = tuple(systems)

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

    def routing(self, i:int, demand:tuple):
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
            system_i = self.get_system_data(i)
            system_i.update_time_states(self.t_now)
            system_i.demands.pop(demand[0])
            system_i.save()
            del system_i
            gc.collect()
            # print(f'\tтребования в {i}: {self.systems[i].current_demands()}')
        if j != 0:
            system_j = self.get_system_data(j)
            system_j.update_time_states(self.t_now)
                # self.systems[j].demands.append(demand)
            system_j.demands[demand[0]] = demand[1]
            system_j.save()
            del system_j
            gc.collect()
                # print(f'\tтребования в {j}: {self.systems[j].current_demands()}')
        else:
            self.serviced_demands += 1
            self.sum_life_time += self.t_now - demand[1]
    
    def restore(self):
        print(f'Сеть восстанавливается при\nb: {self.b}')
        self.b = [1] * self.L
        self.theta = np.copy(self.initial_theta)
        for i in range(1, self.L + 1):
            # print(system.gamma)
            system = self.get_system_data(i)
            system.be_destroyed_at = self.t_now + system.destroy_time()
            system.save()
            del system
            gc.collect()


    def get_system_data(self, system_id:int, *args) -> QueueingSystem:
        system = QueueingSystem(system_id=system_id)
        system.load()
        return system
        # if args...

    def put_system_data(self, system_id:int):
        system = QueueingSystem(system_id=system_id)
        system.save()

    def simulation(self):
        demand_id = 0
        while self.t_now < self.t_max:
            print(f'{self.t_now}')
            for i in range(1, self.L + 1):
                system = self.get_system_data(i)
                print(f'{system.id}\n\t{system.time_states}\n\t{len(system.demands)}')
                del system
                gc.collect()
            self.indicator = False

            # генерация требования
            if (self.t_processes[0] == self.t_now):
                self.indicator = True
                self.t_processes[0] = self.t_now + self.arrival_time()
                demand_id += 1
                demand = (demand_id, self.t_now)
                self.total_demands += 1
                print(f'\tтребование {demand_id} поступило в сеть')
                self.routing(0, demand)

            for i in range(1, self.L + 1):
                # начало обслуживания
                system = self.get_system_data(i)

                if system.service_flag == False and len(system.demands) > 0:
                    self.indicator = True
                    system.service_flag = True
                    self.t_processes[i] = self.t_now + system.service_time()
                    fk = next(iter(system.demands))
                    print(f'\tтребование {fk} начало обслуживаться в системе {i}')

                # завершение обслуживания
                if self.t_processes[i] == self.t_now:
                    self.indicator = True
                    system.service_flag = False
                    fk = next(iter(system.demands))
                    print(f'\tтребование {fk} закончило обслуживаться в системе {i}')
                    self.routing(i, (fk, system.demands[fk]))
                    self.tau = self.sum_life_time / self.serviced_demands if self.serviced_demands != 0 else 0
                    self.t_processes[i] = self.t_max + 1

                # выход из строя
                if system.be_destroyed_at == self.t_now:
                    print(f'Система {i} выходит из строя')
                    system.state = False
                    self.lost_demands += len(system.demands)
                    print(system.current_demands())
                    system.demands.clear()
                    self.b[i - 1] = 0
                    system.be_destroyed_at = self.t_max + 1
                    self.t_processes[i] = self.t_max + 1
                    self.theta = self.change_theta()
                    if not self.check_matrix():
                        self.restore()
                    self.tau_summarized += self.sum_life_time / self.serviced_demands if self.serviced_demands != 0 else 0
                    self.count_states += 1
                    self.serviced_demands = 0
                    self.sum_life_time = 0
                
                system.save()
                del system
                gc.collect()

            if self.tau > self.tau_threshold:
                self.restore()
                self.tau_summarized += self.sum_life_time / self.serviced_demands if self.serviced_demands != 0 else 0
                self.count_states += 1
                self.serviced_demands = 0
                self.sum_life_time = 0


            if not self.indicator:
                # статистика
                systems_destruction = [0]*self.L
                for i in range(1, self.L + 1):
                    system = self.get_system_data(i)
                    system.update_time_states(self.t_now)
                    systems_destruction[i - 1] = system.be_destroyed_at
                    system.save()
                    
                    del system
                    gc.collect()
                
                print('------')
                print(f'tau for {self.b} = {self.tau}')
                for i in range(self.L + 1):
                    system = self.get_system_data(i)
                    print(f'Система {i}:\n{[state / self.t_max for state in system.time_states]}')
                    del system
                    gc.collect()
                print('------\n')

                self.t_old = self.t_now
                self.t_now = min(self.t_processes + systems_destruction)
            


        print(f'\nВсего требований: {self.total_demands}\nОбслужено {self.total_demands - self.lost_demands}, потеряно {self.lost_demands}')
        print(f'tau = {self.tau_summarized / self.count_states if self.tau_summarized != 0 else self.tau}')
        print(f'p_lost = {self.lost_demands / self.total_demands}')
        print("p:")
        for i in range(self.L + 1):
            system = self.get_system_data(i)
            system.load()
            print(f'\tСистема {i}:{sum([state / self.t_max for state in system.time_states])}')
            print(f'\tСистема {i}:\n\t{[state / self.t_max for state in system.time_states]}\n')
            del system
            gc.collect()



