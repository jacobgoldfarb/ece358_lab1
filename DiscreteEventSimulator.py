import queue
import time
import threading
from NumberGenerator import NumberGenerator
from Event import Event


class DiscreteEventSimulator:

    # 0 capacity corresponds to infinite queue size
    def __init__(self, capacity=0, transmission_rate=1_000_000, simulation_time=1_000):
        self.transmission_rate = transmission_rate
        self.capacity = capacity
        self.simulation_time = simulation_time

        self.packet_queue = queue.Queue(capacity)
        self.num_packets_lost = 0
        self.num_packets_passed = 0
        self.queueing_delay = 0
        self.events = []
        self.observer_events = []
        self.dropped_events = []
        self.all_events = []

    def __repr__(self):
        return "Arrival Time\t\tService Time\t\tDeparture\t\tPacket Length\t\tQueue Size\n" + "".join(
            [f"{event.arrival_time}\t"
             f"{event.service_time}\t"
             f"{event.departure_time}\t"
             f"{event.packet_length}\t"
             f"{event.queue_size}\n"
             for
             event in self.events]) + f" Dropped Events: {len(self.dropped_events)}\n " \
                                      f"Succeeded Events: {len(self.events)} \n"

    def create_table(self, num_packets, arrival_rate, observer_rate):
        return self.generate_events(num_packets, arrival_rate, observer_rate)

    def generate_events(self, arrival_rate, average_packet_length, observer_rate):
        self.generate_packet_events(arrival_rate, average_packet_length)
        self.simulate()
        return self.generate_observer_events(observer_rate)

    def generate_packet_events(self, arrival_rate, average_packet_length):
        self.events = [Event(
            arrival_time=NumberGenerator.poisson(arrival_rate),  # length/arrival rate
            length=NumberGenerator.poisson(1 / average_packet_length),
            transmission_rate=self.transmission_rate
        )]
        self.events[0].departure_time = self.events[0].arrival_time + self.events[0].service_time
        i = 1
        while self.events[-1].arrival_time < self.simulation_time:
            prev_event = self.events[i - 1]
            new_event = Event(
                arrival_time=prev_event.arrival_time + NumberGenerator.poisson(arrival_rate),
                length=NumberGenerator.poisson(1 / average_packet_length),
                transmission_rate=self.transmission_rate
            )
            self.events.append(new_event)
            i += 1

    def generate_observer_events(self, observer_rate):
        self.observer_events = [Event(arrival_time=NumberGenerator.poisson(observer_rate))]
        i = 1
        while self.observer_events[-1].arrival_time < self.simulation_time:
            prev_event = self.observer_events[i - 1]
            new_event = Event(
                arrival_time=prev_event.arrival_time + NumberGenerator.poisson(observer_rate),
            )
            self.observer_events.append(new_event)
            i += 1
        return self.get_observer_avg_num_packets_in_q()

    def get_observer_avg_num_packets_in_q(self):
        num_arrivals = 0
        num_departed = 0
        all_events = self.get_sorted_events()
        total_q_size = 0
        for event in all_events:
            if event[0] == 'Arrival':
                num_arrivals += 1
            elif event[0] == 'Departure':
                num_departed += 1
            else: # Observer
                queue_size = num_arrivals - num_departed
                total_q_size += queue_size
        return total_q_size / len(self.observer_events)

    def get_sorted_events(self):
        arrival_events = [('Arrival', event.arrival_time) for event in self.events]
        departure_events = [('Departure', event.departure_time) for event in self.events]
        observer_events = [('Observer', event.arrival_time) for event in self.observer_events]
        sorted_events = sorted(observer_events + departure_events + arrival_events, key=lambda x: x[1])
        return sorted_events

    def num_packets_in_q(self, at_time):
        return len([0 for event in self.events if event.arrival_time < at_time < event.departure_time])

    def simulate(self):
        # Set departure times
        i = 1
        while i < len(self.events):
            prev_event = self.events[i - 1]
            cur_event = self.events[i]
            should_enqueue = prev_event.departure_time > cur_event.arrival_time
            if self.packet_queue.full():
                cur_event.dropped = True
                self.dropped_events.append(self.events.pop(i))
                # Don't increment so we don't skip any events
            elif should_enqueue:
                cur_event.departure_time = prev_event.departure_time + cur_event.service_time
                self.packet_queue.put(cur_event.departure_time)
                cur_event.queue_size = self.packet_queue.qsize()
                i += 1
            else:
                cur_event.departure_time = cur_event.arrival_time + cur_event.service_time
                i += 1
            self.move_queue(cur_event.arrival_time)

    def move_queue(self, cur_time):
        if self.packet_queue.empty():
            return
        while self.packet_queue.empty() and not self.packet_queue.queue[0] < cur_time:
            self.packet_queue.get(False)
