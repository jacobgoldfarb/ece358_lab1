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
    des = DiscreteEventSimulator(service_rate=500)
    # expected number of packets per second
    arrival_rate = 10
    num_packets = 50
    des.create_table(num_packets, arrival_rate)

def run_MM1k_simul(k=10):
    des = DiscreteEventSimulator(capacity=k, service_rate=500)
    # expected number of packets per second
    arrival_rate = 10
    num_packets = 50
    des.create_table(num_packets, arrival_rate)
    mean, var = get_stats()
    print(f"approximate lambda: {1/mean}")
    # print(des)

def get_stats(num_trials=100000, lambd=75):
    random_vars = [NumberGenerator.poisson(lambd) for _ in range(0, num_trials)]
    mean = sum(random_vars) / num_trials
    variance = sum([(var - mean) ** 2 for var in random_vars]) / num_trials
    return mean, variance


if __name__ == "__main__":
    main()
