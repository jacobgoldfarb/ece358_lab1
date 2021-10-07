from NumberGenerator import NumberGenerator
from Utility import Utility
from DiscreteEventSimulator import DiscreteEventSimulator
import matplotlib.pyplot as plt

from multiprocessing.pool import ThreadPool


def main():
    run_MM1_simul()
    # run_MM1k_simul()


def run_MM1_simul():
    rhos = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    transmission_rate = 1_000_000
    avg_packet_length = 2000
    des = DiscreteEventSimulator(transmission_rate=transmission_rate, simulation_time=100)
    avg_packet_for_all_rhos = []

    for i, rho in enumerate(rhos[:]):
        print(f"Iteration {i}, rho: {rho}")
        arrival_rate = Utility.get_arrival_rate_from_rho(rho)
        print(f"Lambda: {arrival_rate}")
        observer_rate = arrival_rate * 5
        avg_q_size = des.create_table(arrival_rate, avg_packet_length, observer_rate)
        print(f"Q size: {avg_q_size}")
        avg_packet_for_all_rhos.append(avg_q_size)
        print(f"Packets generated: {len(des.events)}")

    plt.plot(rhos, avg_packet_for_all_rhos)
    plt.show()


def run_MM1k_simul():
    Ks = [10, 25, 50]
    rhos = [float(i)/10.0 for i in range(5, 15 + 1)]
    print(rhos)
    transmission_rate = 1_000_000
    avg_packet_length = 2000
    avg_packets_in_q_for_all_ks = []
    avg_packet_loss_for_all_ks = []
    avg_packets_in_q_for_all_ks
    for i, k in enumerate(Ks):
        des = DiscreteEventSimulator(capacity=k, transmission_rate=transmission_rate, simulation_time=50)
        avg_packet_in_q_for_all_rhos = []
        avg_packet_loss_for_all_rhos = []

        for j, rho in enumerate(rhos):
            print(f"Iteration {i}-{j}, k: {k}, rho: {rho}")
            arrival_rate = Utility.get_arrival_rate_from_rho(rho)
            print(f"Lambda: {arrival_rate}")
            observer_rate = arrival_rate * 5
            avg_q_size = des.create_table(arrival_rate, avg_packet_length, observer_rate)
            avg_packet_in_q_for_all_rhos.append(avg_q_size)
            avg_packet_loss_for_all_rhos.append(des.proportion_of_lost_packets())
            print(f"Packets generated: {des.total_num_packets()}")
            print(f"Proportion of packets lost: {avg_packet_loss_for_all_rhos[-1]}")
            # des.print_sorted_events(True)
        avg_packets_in_q_for_all_ks.append(avg_packet_in_q_for_all_rhos)
        avg_packet_loss_for_all_ks.append(avg_packet_loss_for_all_rhos)

    plt.figure(1)
    for i, k in enumerate(Ks):
        plt.plot(rhos, avg_packet_loss_for_all_ks[i], label=str(k))
    plt.title("Average packet loss for all K values:")
    plt.legend()

    plt.figure(2)
    for i, k in enumerate(Ks):
        plt.plot(rhos, avg_packets_in_q_for_all_ks[i], label=str(k))
    plt.title("Average packets in queue for all K values:")
    plt.show()

def get_stats(num_trials=100000, lambd=75):
    random_vars = [NumberGenerator.poisson(lambd) for _ in range(0, num_trials)]
    mean = sum(random_vars) / num_trials
    variance = sum([(var - mean) ** 2 for var in random_vars]) / num_trials
    return mean, variance


if __name__ == "__main__":
    main()
