import pickle
from math import log, prod
from numpy import random

class QueueingSystem:
    serviced_demands = dict()
    # {id_demand:
    #       (arrival_time, begin_service, end_service, from_id, where_id)}

    def __init__(self, id:int, server_cnt:int, mu:float, gamma:float, queue_length:int=10, state:bool=True, k:int=1) -> None:
        self.id = id
        self.server_cnt = server_cnt
        self.mu = mu
        self.queue_length = queue_length
        self.gamma = gamma
        self.state = state
        self.k = k
    
    def service_time(self):
        return -log(prod([random.random() for _ in range(self.k)])) / self.mu
    
    def destroy_time(self):
        return -log(random.random()) / self.gamma
    
    def serialization(self):
        with open(f'system_{id}.pickle', 'wb') as f:
            pickle.dump(self.serviced_demands, f)
    
    def deserialization(self):
        with open(f'system_{id}.pickle', 'rb') as f:
            self.serviced_demands = pickle.load(f)


class OuterQueueingSystem(QueueingSystem):
    def __init__(self, id: int, lambda_0:float, server_cnt: int, mu: float, gamma: float, queue_length: int = 10, state: bool = True, k: int = 1) -> None:
        super().__init__(id, server_cnt, mu, gamma, queue_length, state, k)
        self.lambda_0 = lambda_0