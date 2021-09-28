import random
import math

class NumberGenerator:

    def __init__(self):
        pass

    @staticmethod
    # lambd is the rate parameter.
    def poisson(lambd=0.5):
        def ln(x): return math.log(x, math.e)
        U = random.random()
        return -(1/lambd) * ln(1 - U)
