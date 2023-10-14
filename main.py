from QueueingNetwork import QueueingNetwork
import numpy as np

if __name__ == '__main__':
    # theta = np.array([
    #     [0, .5, 0, 0, .5],
    #     [.5, 0, 0, .5, 0],
    #     [.5, .5, 0, 0, 0],
    #     [0, 0, .5, 0, .5],
    #     [0, 0, 1, 0, 0]
    # ])
    # mu = (.5, .3, .6, .2)
    # gamma = (.01, .02, .01, .02)
    theta = np.array([
        [0, .5, .5],
        [.5, 0, .5],
        [.5, .5, 0,]
    ])
    mu = (1.5, 1.3)
    gamma = (.01, .02)
    lambda_0 = 1.
    nw = QueueingNetwork(10, len(mu), lambda_0, theta, mu, gamma)
    nw.simulation()