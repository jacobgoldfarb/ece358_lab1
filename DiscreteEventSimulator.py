from collections import deque
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

        self.packet_queue = deque()
        self.proportion_lost = 0
        self.events = []
        self.observer_events = []
        self.dropped_events = []

    def __repr__(self):
        return "Arrival Time\t\tService Time\t\tDeparture\t\tPacket Length\n" + "".join(
            [f"{event.arrival_time}\t"
             f"{event.service_time}\t"
             f"{event.departure_time}\t"
             f"{event.packet_length}\n"
             for
             event in self.get_all_sorted_events()]) + f" Dropped Events: {len(self.dropped_events)}\n " \
                                      f"Succeeded Events: {len(self.get_sorted_events())} \n"

    def total_num_packets(self):
        return float(len(self.events) + len(self.dropped_events))

    def proportion_of_lost_packets(self):
        # return len(self.dropped_events) / (len(self.dropped_events) + len(self.events))
        return self.proportion_lost

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

    def print_sorted_events(self, include_dropped=False):
        events = self.get_sorted_events()
        if include_dropped:
            dropped = [('Dropped', event.arrival_time) for event in self.dropped_events]
            events = sorted(events + dropped, key=lambda event: event[1])
        num_arrivals = 0
        num_departures = 0
        for event in events:
            if event[0] == 'Arrival':
                num_arrivals += 1
            elif event[0] == 'Departure':
                num_departures += 1
            q_size = num_arrivals - num_departures
            print(f"{event[0]}: {event[1]} {q_size}")

    def generate_observer_events(self, observer_rate):
        self.observer_events = [Event(arrival_time=NumberGenerator.poisson(observer_rate))]
        i = 1
        while self.observer_events[-1].arrival_time < self.events[-1].departure_time:
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
        num_packets_lost = 0
        num_packets_passed = 0
        packet_success_proportions = []
        all_events = self.get_sorted_events(include_dropped=False)
        total_q_size = 0
        q_size_average = 0.0
        num_observers = len(self.observer_events)
        for event in all_events:
            if event[0] == 'Arrival':
                num_arrivals += 1
                num_packets_passed += 1
            elif event[0] == 'Dropped':
                num_packets_lost += 1
            elif event[0] == 'Departure':
                num_departed += 1
            else:  # Observer
                new_prop = 0
                num_packets_in_q = num_arrivals - num_departed
                if num_packets_passed > 0 or num_packets_lost > 0:
                    new_prop = num_packets_lost / (num_packets_passed + num_packets_lost)
                packet_success_proportions.append(new_prop)
                if self.capacity != 0:
                    num_packets_in_q = min(num_packets_in_q, self.capacity)
                q_size_average += num_packets_in_q / num_observers
                # total_q_size += num_packets_in_q
        self.proportion_lost = sum(packet_success_proportions) / len(self.observer_events)
        return q_size_average # total_q_size / len(self.observer_events)

    # Includes droppped events
    def get_all_sorted_events(self):
        events = self.dropped_events + self.events
        return sorted(events, key=lambda event: event.arrival_time)

    def get_sorted_events(self, include_dropped=False):
        arrival_events = [('Arrival', event.arrival_time) for event in self.events]
        departure_events = [('Departure', event.departure_time) for event in self.events]
        observer_events = [('Observer', event.arrival_time) for event in self.observer_events]
        if include_dropped:
            dropped_events = [('Dropped', event.arrival_time) for event in self.dropped_events]
            arrival_events += dropped_events
        sorted_events = sorted(observer_events + departure_events + arrival_events, key=lambda x: x[1])
        return sorted_events

    def simulate(self):
        # Set departure times
        i = 1
        while i < len(self.events):
            prev_event = self.events[i - 1]
            cur_event = self.events[i]
            should_enqueue = prev_event.departure_time > cur_event.arrival_time
            # print(f"Q size: {self.packet_queue.qsize()}")
            if 0 < self.capacity <= len(self.packet_queue):
                cur_event.dropped = True
                self.dropped_events.append(self.events.pop(i))
                # Don't increment so we don't skip any events
            elif should_enqueue:
                cur_event.departure_time = prev_event.departure_time + cur_event.service_time
                self.packet_queue.append(cur_event.departure_time)
                i += 1
            else:
                cur_event.departure_time = cur_event.arrival_time + cur_event.service_time
                i += 1
            self.move_queue(cur_event.arrival_time)

    # dequeues all packets with departure_time < cur_time
    def move_queue(self, cur_time):
        self.packet_queue = deque(sorted(self.packet_queue))
        if len(self.packet_queue) == 0:
            return
        while len(self.packet_queue) > 0 and self.packet_queue[0] < cur_time:
            self.packet_queue.popleft()
