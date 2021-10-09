from Utility import Utility
from DiscreteEventSimulator import DiscreteEventSimulator
import matplotlib.pyplot as plt

def main():
    run_MM1_simul()
    # run_MM1k_simul()
    # debug_MM1k_simul()
    # print(get_stats())


def run_MM1_simul():
    rhos = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.2]
    transmission_rate = 1_000_000
    avg_packet_length = 2000
    avg_packet_for_all_rhos = []
    avg_packet_idle_for_all_rhos = []

    for i, rho in enumerate(rhos[:]):
        des = DiscreteEventSimulator(transmission_rate=transmission_rate, simulation_time=1000)
        print(f"Iteration {i}, rho: {rho}")
        arrival_rate = Utility.get_arrival_rate_from_rho(rho)
        observer_rate = arrival_rate * 5
        avg_q_size = des.run(arrival_rate, avg_packet_length, observer_rate)
        avg_packet_for_all_rhos.append(avg_q_size)
        avg_packet_idle_for_all_rhos.append(des.q_idle_proportions)

    plt.figure(1)
    plt.plot(rhos, avg_packet_for_all_rhos)
    plt.title("Average packets in queue vs. utilization:")
    plt.xlabel("utilization")
    plt.ylabel("average number of packets lost")
    plt.show()

    plt.figure(2)
    plt.plot(rhos, avg_packet_idle_for_all_rhos)
    plt.title("Queue idle time vs. utilization:")
    plt.xlabel("utilization")
    plt.ylabel("average number of packets lost")
    plt.show()

def run_MM1k_simul():
    Ks = [10, 25, 50]
    rhos = [float(i) / 10.0 for i in range(5, 15 + 1)]
    print(rhos)
    transmission_rate = 1_000_000
    avg_packet_length = 2000
    avg_packets_in_q_for_all_ks = []
    avg_packet_loss_for_all_ks = []
    avg_packets_in_q_for_all_ks
    for i, k in enumerate(Ks):
        avg_packet_in_q_for_all_rhos = []
        avg_packet_loss_for_all_rhos = []
        for j, rho in enumerate(rhos):
            des = DiscreteEventSimulator(capacity=k, transmission_rate=transmission_rate, simulation_time=1000)
            arrival_rate = Utility.get_arrival_rate_from_rho(rho)
            print(f"Iteration {i}-{j}, k: {k}, rho: {rho}, lambda: {arrival_rate}")
            observer_rate = arrival_rate * 5
            avg_q_size = des.run(arrival_rate, avg_packet_length, observer_rate)
            avg_packet_in_q_for_all_rhos.append(avg_q_size)
            avg_packet_loss_for_all_rhos.append(des.proportion_of_lost_packets())

        avg_packets_in_q_for_all_ks.append(avg_packet_in_q_for_all_rhos)
        avg_packet_loss_for_all_ks.append(avg_packet_loss_for_all_rhos)

    plt.figure(1)
    for i, k in enumerate(Ks):
        plt.plot(rhos, avg_packet_loss_for_all_ks[i], label=str(k))
    plt.title("Average packet loss vs. utilization for all queue sizes:")
    plt.xlabel("utilization")
    plt.ylabel("proportion of packets lost")
    plt.legend()

    plt.figure(2)
    for i, k in enumerate(Ks):
        plt.plot(rhos, avg_packets_in_q_for_all_ks[i], label=str(k))
    plt.title("Average packets in queue vs. utilization for all K values:")
    plt.xlabel("utilization")
    plt.ylabel("average number of packets lost")
    plt.legend()
    plt.show()


def get_stats(num_trials=100000, lambd=75):
    random_vars = [Utility.poisson(lambd) for _ in range(0, num_trials)]
    mean = sum(random_vars) / num_trials
    variance = sum([(var - mean) ** 2 for var in random_vars]) / num_trials
    return mean, variance


if __name__ == "__main__":
    main()
