import pickle
from math import log, prod
from numpy import random
from Demand import Demand

class QueueingSystem:
    def __init__(self, id:int, server_cnt:int, mu:float, gamma:float, state:bool=True, k_mu:int=1, k_gamma:int=1, time_states:list=[0]) -> None:
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

        # длительности пребывания в состояних
        self.time_states = time_states

        self.save()
    
    def service_time(self):
        return -log(prod([random.random() for _ in range(self.k_mu)])) / self.mu
    
    def destroy_time(self):
        return -log(prod([random.random() for _ in range(self.k_gamma)])) / self.gamma

    def save(self):
        with open(f'system_{self.id}.pickle', 'wb') as f:
            pickle.dump({
                'id' : self.id,
                'server_cnt' : self.server_cnt,
                'mu' : self.mu,
                'k_mu' : self.k_mu,
                'gamma' : self.gamma,
                'k_gamma' : self.k_gamma,
                'be_destroyed_at' : self.be_destroyed_at,
                'state' : self.state,
                'service_flag' : self.service_flag,
                'demands' : self.demands,
                'last_state' : self.last_state,
                'time_states' : self.time_states
            }, f)
    
    def load(self):
        with open(f'system_{self.id}.pickle', 'rb') as f:
            data = pickle.load(f)
            self.id = data['id']
            self.server_cnt = data['server_cnt']
            self.mu = data['mu']
            self.k_mu = data['k_mu']
            self.gamma = data['gamma']
            self.k_gamma = data['k_gamma']
            self.be_destroyed_at = data['be_destroyed_at']
            self.state = data['state']
            self.service_flag = data['service_flag']
            self.demands = data['demands']
            self.last_state = data['last_state']              
        
    def current_demands(self):
        return [item.id for item in self.demands]
    
    def update_time_states(self, t_now:float):
        if len(self.time_states) <= len(self.demands) + 1:
            self.time_states.extend([0])

        try:
            self.time_states[len(self.demands)] += t_now - self.last_state
        except IndexError:
            print(self.id, self.time_states, len(self.demands), self.last_state)
            raise IndexError
        
        self.last_state = t_now
