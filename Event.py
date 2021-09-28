from datetime import datetime
from NumberGenerator import NumberGenerator


class Event:

    def __init__(self,
                 arrival_time,
                 service_time,
                 type='Arrival'):
        self.type = type
        self.arrival_time = arrival_time
        self.departure_time = 0
        self.service_time = service_time
        self.length = NumberGenerator.poisson(5)

