# описание требования
class Demand:
    def __init__(self, id:int, arrival:float=0, exit:float=0):
        self.id = id
        # момент поступления в сеть
        self.arrival = arrival
        # момент выхода из сети 
        self.exit = exit
        # список посещенных узлов сети
        self.nodes = list()