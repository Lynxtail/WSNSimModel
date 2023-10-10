from math import log
import numpy as np

class QueueingNetwork:

    def __init__(self, t_max:int, L:int, lambda_0:float, theta:np.ndarray) -> None:
        self.t_max = t_max
        self.L = L
        self.lambda_0 = lambda_0
        self.t_now = 0
        self.theta = theta
        self.indicator = False
        self.t_act_source = 0
        
        tmp = list()
        for i in range(L + 1):
            if theta[0][i] > 0:
                tmp.append(i)
        self.outer_systems = tuple(tmp)

        tmp = list()
        for i in range(L + 1):
            if theta[i][0] > 0:
                tmp.append(i)
        self.end_systems = tuple(tmp)

    def arrival_time(self):
        return self.t_now + -log(np.random.random()) / self.lambda_0

    def simulation(self):
        # try:
            while self.t_now < self.t_max:
                self.indicator = False

                if (self.t_act_source == self.t_now):
                    self.indicator = True
                    self.t_act_source = self.arrival_time()