from QueueingNetwork import QueueingNetwork
import numpy as np

if __name__ == '__main__':
    theta = np.array([
        [0, .25, 0, 0, .25, 0, .25, 0, .25],
        [0, 0, .5, 0, .5, 0, 0, 0, 0],
        [0, 0, 0, .5, .5, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, .5, 0, .5, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, .5, .5, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0]
    ])
    mu = (5, 1.8, 1., 1.7, 1., 1.9, 1.2, 3.1)
    gamma = (.01, .02, .04, .03, .01, .02, .04, .03)

    # theta = np.array([
    #     [0, .5, .5],
    #     [.5, 0, .5],
    #     [.5, .5, 0,]
    # ])
    # mu = (1.5, 1.3)
    # gamma = (.01, .02)
    lambda_0 = 1.5
    nw = QueueingNetwork(10**1, len(mu), lambda_0, theta, mu, gamma)
    nw.simulation()