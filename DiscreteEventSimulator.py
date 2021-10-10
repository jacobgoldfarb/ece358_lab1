from collections import deque
from Utility import Utility
from Event import Event


class DiscreteEventSimulator:

    # 0 capacity corresponds to infinite queue size
    def __init__(self, capacity=0, transmission_rate=1_000_000, simulation_time=1_000):
        self.transmission_rate = transmission_rate
        self.capacity = capacity
        self.simulation_time = simulation_time

        # Double-ended queue to be updated as packets are enqueued and dequeued.
        self.packet_queue = deque()

        # Event storage
        self.events = []
        self.observer_events = []
        self.dropped_events = []

        # Metrics to be calculated by looping through observers.
        self.proportion_lost = 0
        self.q_idle_proportions = 0
        self.avg_q_size = 0

    def total_num_packets(self):
        return float(len(self.events) + len(self.dropped_events))

    def proportion_of_lost_packets(self):
        return self.proportion_lost

    # Wrapper to generate events, determines departure times, dropped packets, and calculates metrics.
    def run(self, num_packets, arrival_rate, observer_rate):
        self.generate_events(num_packets, arrival_rate, observer_rate)

    # Generates events, determines departure times, dropped packets, and calculates metrics.
    def generate_events(self, arrival_rate, average_packet_length, observer_rate):
        self.generate_packet_events(arrival_rate, average_packet_length)
        self.simulate()
        self.generate_observer_events(observer_rate)

    # Generate arrival times for all packet events in the simulation. The dropped events
    # and departure times are calculated separately, in the simulation function.
    def generate_packet_events(self, arrival_rate, average_packet_length):
        self.events = [Event(
            arrival_time=Utility.poisson(arrival_rate),  # length/arrival rate
            length=Utility.poisson(1 / average_packet_length),
            transmission_rate=self.transmission_rate
        )]
        self.events[0].departure_time = self.events[0].arrival_time + self.events[0].service_time
        i = 1
        # Stop when we have generated a packet with arrival time greater than or equal to the simulation time.
        while self.events[-1].arrival_time < self.simulation_time:
            prev_event = self.events[i - 1]
            new_event = Event(
                arrival_time=prev_event.arrival_time + Utility.poisson(arrival_rate),
                length=Utility.poisson(1 / average_packet_length),
                transmission_rate=self.transmission_rate
            )
            self.events.append(new_event)
            i += 1

    # Generates all observer events based on the rate. We only care about the arrival time, since
    # these are not packets.
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
        self.calculate_metrics_using_observers()

    def calculate_metrics_using_observers(self):
        num_arrivals = 0
        num_departed = 0
        num_packets_lost = 0
        num_packets_passed = 0
        packet_loss_proportions = 0

        all_events = self.get_sorted_events(True)
        local_q_idle_proportions = 0
        total_q_size = 0
        num_observers = len(self.observer_events)

        for event in all_events:
            # Increment arrivals and passed packets
            num_packets_in_q = num_packets_passed - num_departed
            if event[0] == 'Arrival':
                num_arrivals += 1
                if num_packets_in_q > self.capacity > 0:
                    num_packets_lost += 1
                else:
                    num_packets_passed += 1
            # Increment departed count
            elif event[0] == 'Departure':
                num_departed += 1
            else:  # Observer, calculate all metrics necessary
                packet_success_proportion = 0
                # num_packets_in_q = num_arrivals - num_departed
                # Avoid divide by zero errors
                if num_packets_passed > 0 or num_packets_lost > 0:
                    packet_success_proportion = num_packets_lost / (num_packets_passed + num_packets_lost)
                packet_loss_proportions += packet_success_proportion
                # capacity = 0 means the simulation is M/M/1
                if self.capacity != 0:
                    num_packets_in_q = min(num_packets_in_q, self.capacity)
                total_q_size += num_packets_in_q
                local_q_idle_proportions += 1 if num_packets_in_q == 0 else 0
        # Set metrics to average based on number of observers
        self.proportion_lost = packet_loss_proportions / num_observers
        self.q_idle_proportions = local_q_idle_proportions / num_observers
        self.avg_q_size = total_q_size / num_observers

    # Includes droppped events
    def get_all_sorted_events(self):
        events = self.dropped_events + self.events
        return sorted(events, key=lambda event: event.arrival_time)

    # Used to calculate metrics.
    # Map the event arrival_time to a tuple ("Arrival", arrival_time) for all events in self.events.
    # Map the event departure_time to a tuple ("Departure", departure_time) for all events in self.events.
    # Map the event arrival_time to a tuple ("Observer", arrival_time) for all events in self.observer_events,
    # here arrival_time is arbitrary -- we just need a time stamp
    # Map the event arrival_time to a tuple ("Dropped", arrival_time) for all events in self.dropped_events.
    def get_sorted_events(self, include_dropped=False):
        arrival_events = [('Arrival', event.arrival_time) for event in self.events]
        departure_events = [('Departure', event.departure_time) for event in self.events]
        observer_events = [('Observer', event.arrival_time) for event in self.observer_events]
        if include_dropped:
            dropped_events = [('Arrival', event.arrival_time) for event in self.dropped_events]
            arrival_events += dropped_events
        sorted_events = sorted(observer_events + departure_events + arrival_events, key=lambda x: x[1])
        return sorted_events

    # Set departure times and dropped_events
    def simulate(self):
        i = 1
        # i can't iterate through events directly since, in the case of M/M/1/k simulations, elements of self.events
        # are popped and moved to the "dropped_events" array.
        while i < len(self.events):
            prev_event = self.events[i - 1]
            cur_event = self.events[i]
            # dequeue all events that have depart_time before cur_event's arrival_time
            self.move_queue(cur_event.arrival_time)
            cur_event.q_size = len(self.packet_queue)
            # Enqueue if queue isn't empty or the last packet hasn't departed yet
            should_enqueue = prev_event.departure_time > cur_event.arrival_time or len(self.packet_queue) > 0
            # If the capcity is not 0 (this represents infinite queue) and the queue size is greater or equal to the
            # capcity, drop the event. Don't increment i, because self.events[i] is already the next event.
            if 0 < self.capacity <= len(self.packet_queue):
                dropped_event = self.events.pop(i)
                self.dropped_events.append(dropped_event)
                # Don't increment so we don't skip any events
            # If we should enqueue the event, but the queue isn't full, update its departure time based on the
            # previous event's departure time. Add it to the queue.
            elif should_enqueue:
                cur_event.was_enqueued = True
                cur_event.departure_time = prev_event.departure_time + cur_event.service_time
                self.packet_queue.append(cur_event.departure_time)
                i += 1
            # Queue is idle, just set the departure time to the arrival_time + service_time
            else:
                cur_event.departure_time = cur_event.arrival_time + cur_event.service_time
                i += 1

    # Dequeues all packets with departure_time < cur_time
    def move_queue(self, cur_time):
        self.packet_queue = deque(sorted(self.packet_queue))
        if len(self.packet_queue) == 0:
            return
        while len(self.packet_queue) > 0 and self.packet_queue[0] < cur_time:
            self.packet_queue.popleft()
