import time
from NumberGenerator import NumberGenerator
from Event import Event
from DiscreteEventSimulator import DiscreteEventSimulator

def main():
    print("Hello World!")
    print(NumberGenerator.poisson(0.1))
    des = DiscreteEventSimulator(10)
    event1 = Event()
    time.sleep(5)
    event2 = Event()
    des.add_event(event1)
    des.add_event(event2)
    print(des.remove_event().time)
    print(des.remove_event().time)



if __name__ == "__main__":
    main()