import time
from NumberGenerator import NumberGenerator
from Event import Event
from DiscreteEventSimulator import DiscreteEventSimulator


def main():
    print("Hello World!")
    print(get_stats())


def get_stats(num_trials=1000, lambd=75):
    random_vars = [NumberGenerator.poisson(lambd) for _ in range(0, num_trials)]
    mean = sum(random_vars) / num_trials
    variance = sum([(var - mean)**2 for var in random_vars]) / num_trials
    return (mean, variance)


if __name__ == "__main__":
    main()
