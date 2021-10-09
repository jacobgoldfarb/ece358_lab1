from collections import deque
from Utility import Utility
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
        self.q_idle_proportions = 0

    def total_num_packets(self):
        return float(len(self.events) + len(self.dropped_events))

    def proportion_of_lost_packets(self):
        return len(self.dropped_events) / (len(self.dropped_events) + len(self.events))
        return self.proportion_lost

    def run(self, num_packets, arrival_rate, observer_rate):
        return self.generate_events(num_packets, arrival_rate, observer_rate)

    def generate_events(self, arrival_rate, average_packet_length, observer_rate):
        self.generate_packet_events(arrival_rate, average_packet_length)
        self.simulate()
        return self.generate_observer_events(observer_rate)

    def generate_packet_events(self, arrival_rate, average_packet_length):
        self.events = [Event(
            arrival_time=Utility.poisson(arrival_rate),  # length/arrival rate
            length=Utility.poisson(1 / average_packet_length),
            transmission_rate=self.transmission_rate
        )]
        self.events[0].departure_time = self.events[0].arrival_time + self.events[0].service_time
        i = 1
        while self.events[-1].arrival_time < self.simulation_time:
            prev_event = self.events[i - 1]
            new_event = Event(
                arrival_time=prev_event.arrival_time + Utility.poisson(arrival_rate),
                length=Utility.poisson(1 / average_packet_length),
                transmission_rate=self.transmission_rate
            )
            self.events.append(new_event)
            i += 1

    def generate_observer_events(self, observer_rate):
        self.observer_events = [Event(arrival_time=Utility.poisson(observer_rate))]
        i = 1
        while self.observer_events[-1].arrival_time < self.events[-1].departure_time:
            prev_event = self.observer_events[i - 1]
            new_event = Event(
                arrival_time=prev_event.arrival_time + Utility.poisson(observer_rate),
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

        all_events = self.get_sorted_events(True)
        local_q_idle_proportions = 0
        total_q_size = 0
        num_observers = len(self.observer_events)

        for event in all_events:
            if event[0] == 'Arrival':
                num_arrivals += 1
                num_packets_passed += 1
            elif event[0] == 'Dropped':
                # num_arrivals += 1
                num_packets_lost += 1
            elif event[0] == 'Departure':
                num_departed += 1
            else:  # Observer
                packet_success_proportion = 0
                num_packets_in_q = num_arrivals - num_departed
                if num_packets_passed > 0 or num_packets_lost > 0:
                    packet_success_proportion = num_packets_lost / (num_packets_passed + num_packets_lost)
                packet_success_proportions.append(packet_success_proportion)
                if self.capacity != 0:
                    num_packets_in_q = min(num_packets_in_q, self.capacity)
                total_q_size += num_packets_in_q
                local_q_idle_proportions += 1 if num_packets_in_q > 0 else 0
                # total_q_size += num_packets_in_q
        self.proportion_lost = sum(packet_success_proportions) / num_observers
        self.q_idle_proportions = local_q_idle_proportions / num_observers
        return total_q_size / num_observers

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

    # Set departure times and dropped_events
    def simulate(self):
        i = 1
        while i < len(self.events):
            prev_event = self.events[i - 1]
            cur_event = self.events[i]
            self.move_queue(cur_event.arrival_time)
            cur_event.q_size = len(self.packet_queue)
            should_enqueue = prev_event.departure_time > cur_event.arrival_time or len(self.packet_queue) > 0
            if 0 < self.capacity <= len(self.packet_queue):
                dropped_event = self.events.pop(i)
                self.dropped_events.append(dropped_event)
                # Don't increment so we don't skip any events
            elif should_enqueue:
                cur_event.was_enqueued = True
                cur_event.departure_time = prev_event.departure_time + cur_event.service_time
                self.packet_queue.append(cur_event.departure_time)
                i += 1
            else:
                cur_event.departure_time = cur_event.arrival_time + cur_event.service_time
                i += 1

    # dequeues all packets with departure_time < cur_time
    def move_queue(self, cur_time):
        self.packet_queue = deque(sorted(self.packet_queue))
        if len(self.packet_queue) == 0:
            return
        while len(self.packet_queue) > 0 and self.packet_queue[0] < cur_time:
            self.packet_queue.popleft()
