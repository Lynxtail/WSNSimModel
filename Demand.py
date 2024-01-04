# описание требования
class Demand:
    def __init__(self, demand_id:int, arrival:float=0, exit:float=0):
        self.id = demand_id
        # момент поступления в сеть
        self.arrival = arrival