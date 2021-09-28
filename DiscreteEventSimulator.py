import queue

class DiscreteEventSimulator:

    def __init__(self, capacity):
        self.buff = queue.Queue(capacity)

    def add_event(self, event):
        self.buff.put(event)

    def remove_event(self):
        return self.buff.get()
