import time
import threading

from NumberGenerator import NumberGenerator
from Event import Event
from DiscreteEventSimulator import DiscreteEventSimulator
from Packet import Packet


def main():
    print("Hello World!")
    print(get_stats())
    run_MM1k_simul()


def run_MM1_simul():
    des = DiscreteEventSimulator(service_rate=2)
    # expected number of packets per second
    arrival_rate = 10
    num_packets = 50
    for i in range(0, num_packets):
        time.sleep(NumberGenerator.poisson(arrival_rate))
        print(f"Added packet {i}")
        new_packet = Packet()
        des.add_packet(new_packet)

def run_MM1k_simul(k=10):
    des = DiscreteEventSimulator(capacity=k, service_rate=500)
    # expected number of packets per second
    arrival_rate = 10
    num_packets = 50
    for i in range(0, num_packets):
        time.sleep(NumberGenerator.poisson(arrival_rate))
        print(f"Added packet {i}")
        new_packet = Packet()
        des.add_packet(new_packet)
    print(f"Loss ratio: {des.loss_ratio()}")

def get_stats(num_trials=1000, lambd=75):
    random_vars = [NumberGenerator.poisson(lambd) for _ in range(0, num_trials)]
    mean = sum(random_vars) / num_trials
    variance = sum([(var - mean) ** 2 for var in random_vars]) / num_trials
    return (mean, variance)


if __name__ == "__main__":
    main()
