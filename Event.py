from datetime import datetime


class Event:

    def __init__(self,
                 type='Departure',
                 time=datetime.now(),
                 length=1):
        self.type = type
        self.time = time
        self.length = length
