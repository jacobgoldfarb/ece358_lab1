import queue
import time
import threading
from NumberGenerator import NumberGenerator
from Event import Event


class DiscreteEventSimulator:

    # 0 capacity corresponds to infinite queue size
    def __init__(self, capacity=0, num_servers=1, service_rate=500):
        self.service_rate = service_rate
        self.num_servers = num_servers
        self.capacity = capacity

        self.num_packets_lost = 0
        self.num_packets_passed = 0
        self.queueing_delay = 0
        self.events = []

    def __repr__(self):
        return "Event\tArrival\tLength (bits)\tService Time\tDeparture\n" + "".join([f"{event.type}\t"
                  f"{event.arrival_time}\t"
                  f"{event.length}\t"
                  f"{event.service_time}\t"
                  f"{event.departure_time}\n" for event in self.events])


    def create_table(self, num_packets, arrival_rate):
        self.generate_events(num_packets, arrival_rate)


    def generate_events(self, num_packets, arrival_rate):
        self.events = [Event(
            arrival_time=NumberGenerator.poisson(arrival_rate),
            service_time=NumberGenerator.poisson(self.service_rate)
        )]
        self.events[0].departure_time = self.events[0].arrival_time + self.events[0].service_time
        for i in range(1, num_packets):
            prev_event = self.events[i - 1]
            new_event = Event(
                arrival_time=prev_event.arrival_time+NumberGenerator.poisson(arrival_rate),
                service_time=NumberGenerator.poisson(self.service_rate)
            )
            self.events.append(new_event)
        self.generate_departure_times(num_packets)

    def generate_departure_times(self, num_packets):
        for i in range(1, num_packets):
            prev_event = self.events[i - 1]
            cur_event = self.events[i]
            queue_idle = prev_event.departure_time < cur_event.arrival_time
            if queue_idle:
                cur_event.departure_time = cur_event.arrival_time + cur_event.service_time
            else:
                cur_event.departure_time = prev_event.departure_time + cur_event.service_time



