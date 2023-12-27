import pickle
from math import log, prod
from numpy import random
from Demand import Demand

class QueueingSystem:
    def __init__(self, id:int, server_cnt:int, mu:float, gamma:float, state:bool=True, k_mu:int=1, k_gamma:int=1) -> None:
        self.id = id
        self.server_cnt = server_cnt
        self.mu = mu
        self.k_mu = k_mu
        self.gamma = gamma
        self.k_gamma = k_gamma

        self.be_destroyed_at = 0
        self.state = state # работоспособна

        self.service_flag = False # свободна
        self.demands = list()
        self.last_state = 0
    
    def service_time(self):
        return -log(prod([random.random() for _ in range(self.k_mu)])) / self.mu
    
    def destroy_time(self):
        return -log(prod([random.random() for _ in range(self.k_gamma)])) / self.gamma

    def serialization_time_states(self, time_states:list()):
        with open(f'system_{self.id}.pickle', 'wb') as f:
            pickle.dump(time_states, f)
    
    def deserialization_time_states(self):
        with open(f'system_{self.id}.pickle', 'rb') as f:
            return pickle.load(f)
        
    def current_demands(self):
        return [item.id for item in self.demands]
    
    def update_time_states(self, t_now:float):
        time_states = self.deserialization_time_states()

        # print(f'\tsystem {self.id} last state: {self.last_state}')

        if len(time_states) <= len(self.demands) + 1:
            time_states.extend([0])

        try:
            time_states[len(self.demands)] += t_now - self.last_state
        except IndexError:
            print(self.id, time_states, len(self.demands), self.last_state)
            raise IndexError
        
        self.last_state = t_now

        self.serialization_time_states(time_states)

