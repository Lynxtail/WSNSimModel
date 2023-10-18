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

        self.be_destroyed_at = 0
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
        time_states = self.deserialization()

        print(f'\tsystem {self.id} last state: {self.last_state}')

        if len(time_states) <= len(self.demands) + 1:
            time_states.extend([0])

        try:
            time_states[len(self.demands)] += t_now - self.last_state
            # time_states[len(self.demands)] += t_now - time_states[self.last_state]
        except IndexError:
            print(self.id, time_states, len(self.demands), self.last_state)
            raise IndexError
        
        # if len(self.demands) != self.last_state:
        #     self.last_state += modifier
        self.last_state = t_now

        self.serialization(time_states)
    
    def continue_time_states(self, t_now:float, t_old:float):
        time_states = self.deserialization()
        if len(time_states) <= len(self.demands) + 1:
                time_states.extend([0, 0])
        time_states[len(self.demands)] += t_now - t_old
        self.serialization(time_states)

