from math import log, prod
import random
import sys
import numpy as np
from Demand import Demand

def run(self):
    
    global t_max
    t_max = 10**4
    lambda_0 = 1
    std_0 = 0
    mu_runway = 6
    std_runway = 0
    mu_parking = 2 
    std_parking = 0    
    self.system = Airport(self, self.ui.spinBox.value(), self.ui.spinBox_4.value(), 
        lambda_0, std_0, mu_runway, self.ui.spinBox_2.value(), 
        std_runway, mu_parking, 
        self.ui.spinBox_3.value(), std_parking, 
        self.ui.comboBox_3.currentText(), self.ui.comboBox.currentText(), 
        self.ui.comboBox_2.currentText(), t_max)

class Network:
    def __init__(self, cnt_runways, cnt_parking, 
    lambda_0, std_0, mu_runway, k_runway, std_runway, mu_parking, k_parking, std_parking, 
    source_distribution, runway_distribution, parking_distribution, t_max):
        self.cnt_runways = cnt_runways
        self.cnt_parking = cnt_parking 
        self.lambda_0 = lambda_0 
        self.std_0 = std_0 
        self.mu_runway = mu_runway
        self.k_runway = k_runway 
        self.std_runway = std_runway 
        self.mu_parking = mu_parking
        self.k_parking = k_parking
        self.std_parking = std_parking
        self.source_distribution = source_distribution
        self.runway_distribution = runway_distribution
        self.parking_distribution = parking_distribution
        self.t_max = t_max

    def generate_random_value(self, type, lambda_:float, std=0, k=1):
        distribution_types = ('Эрланга', 'Нормальное', 'Константа')
        # Эрланга или экспоненциальное (при k = 1)
        if type == distribution_types[0]:
            return -log(prod([random.random() for _ in range(k)])) / lambda_
        # нормальное
        elif type == distribution_types[1]:
            tmp = lambda_ + std * (sum([random.random() 
                for _ in range(12)]) - 6)
            if tmp < 0: tmp = 0.001
            return tmp
        # постоянная величина
        elif type == distribution_types[2]:
            return lambda_
        else:
            print(type)
            raise Exception

    def start_collecting_data(self):
        # очистка логов (сериализация?)
        times = open('times_1.txt', 'w')
        times.close()
        times = open('times_2.txt', 'w')
        times.close()
        demands_out = open('demands_out_1.txt', 'w')
        demands_out.close()
        demands_out = open('demands_out_2.txt', 'w')
        demands_out.close()

    def initialize(self):
        # инициализация моментов активации процессов и вспомогательных величин
        t_act_source = 0 # момент генерации требования
        t_act_device_runway = [t_max + 0.0000001]*self.cnt_runways # момент начала обслуживания на взлётке
        t_act_device_parking = [t_max + 0.0000001]*self.cnt_parking # моменты начала обслуживания приборами на стоянке
        runway_queue_demands = [] # требования в очереди на взлётке
        parking_queue_demands = [] # требования в очереди на парковке
        runway_service_demands = [] # требования на приборах на взлётке 
        parking_service_demands = [] # требования на приборах на парковке
        times = [[0, 0, 0], [0, 0, 0]] # длительности в системах
    
    def arrival(self):
        cnt += 1
        # print(f"Самолёт {cnt}; Момент формирования требования: {t_now}")
        indicator = True
        runway_queue_demands.append(Demand(cnt, False, t_now, t_now))
        t_act_source = t_now + self.generate_random_value(self.source_distribution, self.lambda_0, self.std_0)
        

    def simulation(self):
        # начальные условия
        t_now = 0 # текущее время
        device_runway_free = [True]*self.cnt_runways # индикаторы занятости приборов на взлётке
        device_parking_free = [True]*self.cnt_parking # индикаторы занятости приборов на стоянке

        serviced_demands = [0, 0] # число обслуженных требований в 1 и 2 системах
        cnt = 0 # номер требования

        try:
            # процесс симуляция
            while t_now < t_max:
                indicator = False # индикатор активности какого-либо процесса
                
                # генерация требования
                if (t_act_source == t_now):
                    self.arrival()

                # начало обслуживания требования прибором стоянки
                elif (any(device_parking_free) and any(parking_queue_demands)):
                    # print(f"Самолёт {parking_queue_demands[0].num}; Момент начала обслуживания прибором стоянки: {t_now}")
                    indicator = True
                    t_act_device_parking[device_parking_free.index(True)] = t_now + self.generate_random_value(self.parking_distribution, self.mu_parking, self.std_parking, self.k_parking)
                    parking_service_demands.append(parking_queue_demands.pop(0))
                    parking_service_demands[-1].begin_service_parking = t_now
                    parking_service_demands[-1].end_service_parking = t_act_device_parking[device_parking_free.index(True)]
                    device_parking_free[device_parking_free.index(True)] = False
                    
                # завершение обслуживания требования прибором стоянки
                if (any(item == t_now for item in t_act_device_parking)):
                    # t_service2[1] = t_now
                    indicator = True
                    device_parking_free[t_act_device_parking.index(t_now)] = True
                    t_act_device_parking[t_act_device_parking.index(t_now)] = t_max + 0.0000001
                    
                    for item in parking_service_demands:
                        if item.end_service_parking == t_now:
                            ind = parking_service_demands.index(item)
                            break
                    
                    if ind > len(parking_service_demands):
                        if parking_service_demands[ind - 1] == t_now:
                            ind -= 1

                    # print(f"Самолёт {parking_service_demands[ind].num}; Момент завершения обслуживания прибором стоянки: {t_now}")
                    application.serve_parking(t_now, parking_service_demands[ind].num)

                    parking_service_demands[ind].end_service_parking = t_now
                    parking_service_demands[ind].queue_runway = t_now
                    
                    serviced_demands[1] += 1
                    
                    _, _, a, b, c = parking_service_demands[ind].calc_times(2)
                    times[1][0] += a
                    times[1][1] += b
                    times[1][2] += c
                    # print(parking_service_demands[ind].calc_times(2))
                    
                    runway_queue_demands.append(parking_service_demands.pop(ind))
                    runway_queue_demands[-1].takeoff = True

                    # print(f"Момент поступления: {t_service2[0]}\nМомент выхода из СМО: {t_now}")
                    
                # переход к следующему моменту
                if not indicator:
                    tmp_1 = 1 if serviced_demands[0] == 0 else serviced_demands[0]
                    tmp_2 = 1 if serviced_demands[1] == 0 else serviced_demands[1]
                    v = [[times[0][0] / tmp_1], [times[1][0] / tmp_2]]
                    w = [[times[0][1] / tmp_1], [times[1][1] / tmp_2]]
                    u = [[times[0][2] / tmp_1], [times[1][2] / tmp_2]]

                    application.update_labels(v, w, u)

                    print(f'Среднее время обслуживания на взлётке: {v[0]}')
                    print(f'Среднее время обслуживания на стоянке: {v[1]}')
                    print(f'Среднее время ожидания на взлётке: {w[0]}')
                    print(f'Среднее время ожидания на стоянке: {w[1]}')
                    print(f'Среднее время пребывания на взлётке: {u[0]}')
                    print(f'Среднее время пребывания на стоянке: {u[1]}')

                    demands_out = open('demands_out_1.txt', 'a')
                    demands_out.write(str(len(runway_service_demands) + len(runway_queue_demands)) + '\n')
                    demands_out.close()
                    demands_out = open('demands_out_2.txt', 'a')
                    demands_out.write(str(len(parking_service_demands) + len(parking_queue_demands)) + '\n')
                    demands_out.close()

                    states = [[], []]
                    p = [[], []]

                    cnt_demands = [[], []] 
                    f = open('demands_out_1.txt', 'r')
                    for line in f:
                        cnt_demands[0].append(line)
                    f.close()
                    f = open('demands_out_2.txt', 'r')
                    for line in f:
                        cnt_demands[1].append(line)
                    f.close()

                    cnt_demands = list(map(sorted, cnt_demands))
                    for item in cnt_demands[0]:
                        if item in states[0]:
                            continue
                        else:
                            states[0].append(item)
                            p[0].append(cnt_demands[0].count(item) / len(cnt_demands[0]))
                    for item in cnt_demands[1]:
                        if item in states[1]:
                            continue
                        else:
                            states[1].append(item)
                            p[1].append(cnt_demands[1].count(item) / len(cnt_demands[1]))
                    for item in p:
                        if len(item) == 0:
                            item.append(1)
                            break
                    print(f'Стационарное распределение:{p}')
                    print(f'check: {sum(p[0])}, {sum(p[1])}')
                    
                    if len(p[0]) > 16:
                        tmp_string = ''
                        for i in range(8):
                            tmp_string += f'{p[0][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        tmp_string += '\n\t...\t\n'
                        for i in range(len(p[0]) - 8, len(p[0])):
                            tmp_string += f'{p[0][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                    else:
                        tmp_string = ''
                        for i in range(len(p[0])):
                            tmp_string += f'{p[0][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                    
                    if len(p[1]) > 16:
                        tmp_string = ''
                        for i in range(8):
                            tmp_string += f'{p[1][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                        tmp_string += '\n\t...\t\n'
                        for i in range(len(p[1]) - 8, len(p[1])):
                            tmp_string += f'{p[1][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'
                    else:
                        tmp_string = ''
                        for i in range(len(p[1])):
                            tmp_string += f'{p[1][i]:.4f} '
                            if (i + 1) % 4 == 0:
                                tmp_string += '\n'

                    n = [[u[0][0] * serviced_demands[0] / t_max], [u[1][0] * serviced_demands[1] / t_max]]
                    print(f'Среднее число требований в сети:{n}')
                    
                    states.clear()
                    p.clear()

                    # переход к следующему событию
                    t_now = min(min(t_act_device_runway), min(t_act_device_parking), t_act_source)
        except:
            print(t_now)
            raise Exception