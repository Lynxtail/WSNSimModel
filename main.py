from matplotlib.pylab import f
import queueing_tool as qt
import numpy as np
import matplotlib.pyplot as plt

# интенсивность
def rate(t:int):
    return 25 + 350 * np.sin(np.pi * t / 2)**2

# функция времени прибытия
def arr_f(t:int, k:int = 1, lambda_0:float = 1.5):
    # тело функции
    # scale = 1.0 / rate_max
    # t = t + exponential(scale)
    # while rate_max * uniform() > rate(t):
    #     t = t + exponential(scale)
    # return t
    # return qt.poisson_random_measure(t, rate, 375)
    return t + -np.log(np.prod([np.random.random() for _ in range(k)])) / lambda_0


# def erlang_distr(lambda_:float, k:int=1):
#     return -np.log(np.prod([np.random.random() for _ in range(k)])) / lambda_

# функция времени обслуживания
def ser_f(t:int, mu:float = 1):
    return t + np.random.exponential(1 / mu)

def service(t:int):
    pass

def main(): 
    # составление списка типов очередей (рёбер) в виде 
    # {номер узла 1:
    #   {номер узла 2: тип ребра}
    # }
    
    # узлы, которые принимают требования: 
    edge_list = {0: 
                 {outer_: 1 for outer_ in list(map(int, np.argwhere(theta[0] > 0)))}}    
    # обычные узлы и узлы, которые возвращают требования в источник
    edge_list.update(
                {i: 
                 {node: 0 if j == 0 and theta[i][j] > 0 else 2
                  for j, node in enumerate(list(map(int, np.argwhere(theta[i] > 0))))}
                for i in range(1, L + 1)})

    # создание графа по маршрутной матрице
    # и типа очередей
    g = qt.adjacency2graph(theta, edge_type=edge_list)
    
    # классы систем (источник + узлы)
    # и их параметры
    q_classes = {1: qt.QueueServer, 2: qt.QueueServer}
    q_args = {
        1: { # среда
            'arrival_f': arr_f,
            'service_f': lambda t : t
        }}
    q_args.update({
        i: { # узлы
            'num_servers': 1,
            'service_f': lambda t, mu_i : t + np.random.exponential(1 / mu_i)
            } 
        }
        for i, mu_i in zip(range(1, L + 1), mu))

    # создание сети
    qn = qt.QueueNetwork(g=g, q_classes=q_classes, q_args=q_args, seed=13)
    
    qn.draw(fname='sim.png')

    qn.initialize(edge_type=1)
    qn.start_collecting_data()
    qn.simulate(t=1.9)
    qn.draw(fname='after_sim.png')
    print(qn.num_events, qn.get_queue_data(), qn.get_agent_data(), sep='\n')



if __name__ == '__main__':
    L = 8
    lambda_0 = np.linspace(0.1, 2, 300)
    threshold_tau_0 = 10
    mu = (5, 1.8, 1., 1.7, 1., 1.9, 1.2, 3.1)
    kappa = (1, 1, 1, 1, 1, 1, 1, 1)
    alpha = (.01, .02, .04, .03, .01, .02, .04, .03)
    theta = np.array([
        [0., 0.25, 0., 0., 0.25, 0., 0.25, 0., 0.25],
        [0., 0., 0.5, 0., 0.5, 0., 0., 0., 0.],
        [0., 0., 0., 0.5, 0.5, 0., 0., 0., 0.],
        [1., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0.5, 0., 0.5, 0.],
        [1., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0.5, 0.5, 0., 0., 0., 0., 0.],
        [1., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 1., 0., 0., 0., 0., 0., 0., 0.]])
    main()