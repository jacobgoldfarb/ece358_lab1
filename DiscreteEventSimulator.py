import queue
import time
import threading
from NumberGenerator import NumberGenerator


class DiscreteEventSimulator:

    # 0 capacity corresponds to infinite queue size
    def __init__(self, capacity=0, num_servers=1, service_rate=500):
        self.service_rate = service_rate
        self.num_servers = num_servers
        self.buff = queue.Queue(capacity)

        self.num_packets_lost = 0
        self.num_packets_passed = 0
        self.queueing_delay = 0

    def add_packet(self, packet):
        print(f"Num items on queue: {self.buff.qsize()}")
        if self.buff.full():
            print("Dropping packet...")
            self.num_packets_lost += 1
            return
        self.buff.put(packet)
        self.service_packet()
        x = threading.Thread(target=self.service_packet)
        x.start()

    def service_packet(self):
        self.simulate_delay()
        print("Serviced Packet")
        self.num_packets_passed += 1
        return self.buff.get()

    def simulate_delay(self):
        delay = NumberGenerator.poisson(self.service_rate)
        self.queueing_delay += delay
        time.sleep(self.queueing_delay)
        self.queueing_delay -= delay

    def loss_ratio(self): return self.num_packets_lost / self.num_packets_passed
