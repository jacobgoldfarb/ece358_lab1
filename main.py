from NumberGenerator import NumberGenerator
from DiscreteEventSimulator import DiscreteEventSimulator
import matplotlib.pyplot as plt

from multiprocessing.pool import ThreadPool

def main():
    print("Hello World!")
    print(get_stats())
    run_MM1_simul()
    # run_MM1k_simul()


def run_MM1_simul():

    # expected number of packets per second
    # rho = L * lambda / C
    # rho * C / L = lambda
    rhos = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    transmission_rate = 1_000_000
    avg_packet_length = 2000
    des = DiscreteEventSimulator(transmission_rate=transmission_rate, simulation_time=1000)
    avg_packet_for_all_rhos = []

    for i, rho in enumerate(rhos):
        print(f"Iteration {i}, rho: {rho}")
        arrival_rate = rho * transmission_rate / avg_packet_length
        observer_rate = arrival_rate * 5
        avg_q_size = des.create_table(arrival_rate, avg_packet_length, observer_rate)
        print(f"Q size: {avg_q_size}")
        avg_packet_for_all_rhos.append(avg_q_size)

    plt.plot(avg_packet_for_all_rhos)
    plt.show()
    print(f"Packets generated: {len(des.events)}")


def run_MM1k_simul(k=10):
    des = DiscreteEventSimulator(capacity=k)
    # expected number of packets per second
    arrival_rate = 10
    avg_packet_length = 2000
    des.create_table(arrival_rate, avg_packet_length)
    mean, var = get_stats()
    print(des)
    # print(des)


def get_stats(num_trials=100000, lambd=75):
    random_vars = [NumberGenerator.poisson(lambd) for _ in range(0, num_trials)]
    mean = sum(random_vars) / num_trials
    variance = sum([(var - mean) ** 2 for var in random_vars]) / num_trials
    return mean, variance


if __name__ == "__main__":
    main()
