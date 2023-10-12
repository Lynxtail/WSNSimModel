import pickle
from math import log, prod
from numpy import random

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
        self.time_states = list()
    
    def service_time(self):
        return -log(prod([random.random() for _ in range(self.k)])) / self.mu
    
    def destroy_time(self):
        return -log(random.random()) / self.gamma
    
    def serialization(self):
        with open(f'system_{id}.pickle', 'wb') as f:
            pickle.dump(self.time_states, f)
    
    def deserialization(self):
        with open(f'system_{id}.pickle', 'rb') as f:
            return pickle.load(f)