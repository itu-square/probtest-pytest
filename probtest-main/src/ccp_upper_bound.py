"""
Determines an upper bound on the number of times to run a probabilistic program
to be sure with 1-epsilon to have covered all outputs of the program.

Contains the method ccp(epsilon,N,P) which takes as parameters an epsilon, 
the number of possible outputs, and a list P of probabilities of the outcome.

The python script can be run with parameters as shown below.
Benchmarking is also included, but must be uncommented to run.

Typical usage example:
    python upper_bound.py 0.05 10
    python upper_bound.py 0.05 4 0.1,0.2,0.3,0.4

Author: Katrine Christensen <katch@itu.dk>
"""

import sys
import numpy as np
from functools import reduce
from decimal import Decimal
import matplotlib.pyplot as plt

def ccp(epsilon,N,P):
    """Returns an upper bound on number of times to run a probabilistic 
    programs to be sure with probability 1-epsilon that we have covered 
    all N outputs given the probabilities P=(p1,p2,...,pN) over the outcomes.

    Solves when the probability that it requires more than k runs of the 
    program to achieve coverage is < epsilon.

    Args:
        epsilon: The specification of how sure we want to be that we have
        achieved coverage.
        N: The size of the output set of type int.
        P: A list of probabilities of type int over the outcome of size N.

    Raises:
        ValueError: When epsilon is smaller than or equal to 0 for N>1.
        ValueError: When N and P is not of the same length.
        ValueError: When N<=1.
        ValueError: When the probabilities do not sum to ≤1.

    Returns:
        Upper bound on the number of times to run the probabilistic program.
    """

    if N>1 and epsilon<=0:
        raise ValueError("epsilon must be greater than 0")
    if N!=len(P):
        raise ValueError("N and P must be of same length")
    if N<1:
        raise ValueError("N must be larger than or equal to 1.")
    if reduce(lambda a, b: Decimal(a)+Decimal(b), P) > 1+1E-3:
        raise ValueError("Probabilities must sum to ≤ 1")
    
    k = N
    sum = epsilon
    while sum>=epsilon:
        sum = 0
        for i in range(0,N):
            sum += (1-P[i])**k
        k +=1
    return k-1  

def main():
    """Runs the method for determining an upper bound on number of times to run
    a probabilistic program to achieve output coverage with high probability.
    Two or three arguments must be provided: an epsilon, size of output set N, 
    and a list of probabilities of the outcome. 

    Raises:
        ValueError: When the script is run with less than four arguments.
    """

    if len(sys.argv)<4:
        raise ValueError("Must provide at least three arguments:"+
                         "an epsilon, the size of the output set and a vector of probabilities")

    epsilon = float(sys.argv[1])
    N = int(sys.argv[2])

    P = np.asarray(sys.argv[3].split(','), dtype=float)
    print(ccp(epsilon,N,P))

if __name__ == "__main__":
    main()
