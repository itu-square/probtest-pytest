from scipy.stats import bernoulli
import pytest

def throw_die():
    """Throws a fair die by calling the recursive state function, 
    starting at state 0.

    Returns:
        int: The value of the thrown die.
    """
    X = bernoulli(0.5)
    return state(X,0)
    
def state(X, i):
    """Recursive function implementing the states of the fair die program.
    In each state, a fair coin is tossed to determine the next state.

    Args:
        X: Random variable for the thrown coin.
        i (int): The current state of the fair die program.

    Returns:
        int: The value of the thrown die.
    """
    if i==0:
        if X.rvs()==1: return state(X,1)
        else: return state(X,2) 
    elif i==1: 
        if X.rvs()==1: return state(X,3)
        else: return state(X,4)
    elif i==2:
        if X.rvs()==1: return state(X,5)
        else: return state(X,6)
    elif i==3:
        if X.rvs()==1: return state(X,1)
        else: return 1
    elif i==4:
        if X.rvs()==1: return 2
        else: return 3
    elif i==5:
        if X.rvs()==1: return 4
        else: return 5
    else:
        if X.rvs(): return state(X,2)
        else: return 6

@pytest.fixture()
def o():
    return throw_die()

def test_Q1_between1and6(o):
    assert o>=1 and o<=6

def test_Q2_even_outcome(o):
    assert o%2==0
