from datetime import datetime
from NumberGenerator import NumberGenerator


class Event:

    def __init__(self,
                 type='Departure',
                 time=datetime.now()):
        self.type = type
        self.time = time
        self.length = NumberGenerator.poisson(5)
