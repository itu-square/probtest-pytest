"""Test suite for the methods for computing k for which P(T<k)<epsilon 
using the coupon collector's problem.

Can be run using pytest:
    pytest method/test_ccp.py

Author: Katrine Christensen <katch@itu.dk>
"""

import sys
from pathlib import Path
sys.path.insert(1, './src')

import ccp_upper_bound
import pytest


def test_upper_bound_deterministic_case():
    """When a program is deterministic, we must only run it 
    once to achieve coverage of all outcomes.
    """
    assert ccp_upper_bound.ccp(0.05,1,[1])==1


def test_upper_bound_k_nondeterministic_case():
    """Even as a probability in p grows arbitrarily small, we must still
    run the program more than once as it is nondeterministic.
    """
    N=2
    p1 = 0.5
    while p1 > 0.01:
        p2 = 1-p1
        assert ccp_upper_bound.ccp(0.05,N,[p1,p2]) >1
        p1 -= 0.01

def test_upper_bound_0_outcomes():
    """Problem not well-defined for programs with 0 outcomes."""
    with pytest.raises(ValueError):
        ccp_upper_bound.ccp(0.05,0,[0.5,0.5])

def test_upper_bound_epsilon_equal_to_0():
    """Problem not well-defined for epsilon=0 when N>1."""
    with pytest.raises(ValueError):
        ccp_upper_bound.ccp(0.0,2,[0.5,0.5])

def test_upper_bound_probabilities_sum_to_more_than_1():
    """Problem not well-defined for programs with an ill-defined 
    probability distribution."""
    with pytest.raises(ValueError):
        ccp_upper_bound.ccp(0.05,2,[0.5,0.51])

def test_upper_bound_probabilities_sum_to_less_than_1():
    """Problem well-defined for the subproblem where probabilities sum to
    less than 1, i.e., where we want coverage of a subset of the outcomes.
    """
    ccp_upper_bound.ccp(0.05,2,[0.5,0.49])

def test_upper_bound_probabilities_length_greater_than_N():
    """The number of outcomes must be the same length as the specified p.
    """
    with pytest.raises(ValueError):
        ccp_upper_bound.ccp(0.05,2,[0.5,0.25,0.25])

def test_upper_bound_probabilities_length_smaller_than_N():
    """The number of outcomes must be the same length as the specified p.
    """
    with pytest.raises(ValueError):
        ccp_upper_bound.ccp(0.05,3,[0.5,0.5])
