import pickle
from math import log, prod
from numpy import random
from Demand import Demand

class QueueingSystem:
    def __init__(self, id:int, server_cnt:int, mu:float, gamma:float, state:bool=True, k:int=1) -> None:
        self.id = id
        self.server_cnt = server_cnt
        self.mu = mu
        self.gamma = gamma
        self.k = k
        self.state = state # работоспособна
        self.service_flag = False # свободна
        self.demands = list()
        self.last_state = 0
    
    def service_time(self):
        return -log(prod([random.random() for _ in range(self.k)])) / self.mu
    
    def destroy_time(self):
        return -log(random.random()) / self.gamma
    
    def serialization(self, time_states:list()):
        with open(f'system_{self.id}.pickle', 'wb') as f:
            pickle.dump(time_states, f)
    
    def deserialization(self):
        with open(f'system_{self.id}.pickle', 'rb') as f:
            return pickle.load(f)
        
    def current_demands(self):
        return [item.id for item in self.demands]
    
    def update_time_states(self, t_now:float, modifier:int=0):
        try:
            time_states = self.deserialization()
            if len(time_states) <= len(self.demands) + 1:
                time_states.extend([0, 0])
            time_states[len(self.demands)] += t_now - time_states[self.last_state]
            if len(self.demands) != self.last_state:
                self.last_state += modifier
            self.serialization(time_states)
        except IndexError:
            print(self.id, time_states, len(self.demands), self.last_state)
            raise IndexError
    
    def continue_time_states(self, t_now:float, t_old:float):
        time_states = self.deserialization()
        if len(time_states) <= len(self.demands) + 1:
                time_states.extend([0, 0])
        time_states[len(self.demands)] += t_now - t_old
        self.serialization(time_states)

