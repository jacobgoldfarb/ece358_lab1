from datetime import datetime


class Event:

    def __init__(self, type='Departure', time=datetime.now()):
        self.type = type
        self.time = time
