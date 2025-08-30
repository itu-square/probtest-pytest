"""Test suite to test policies on small frozen lake environment (4x4 board).

The agent moves stochastically where the probability of going in the 
intended direction is 1/3 and the probability of going in the 
perpendicular directions is 2/3.

Settings of the tests can be changed in the setup() fixture. For examle,
the number of episodes of traning (n_episodes) and the number of steps
of the walk in each test (steps).

Can be run with pytest:
    pytest case_studies/frozen_lake
And with probtest:
    pytest case_studies/frozen_lake --probtest --Pbug 0.1

If the -s flag is enabled, the policy is printed as well as an evaluation of
the policy.

Author: Katrine Christensen, katch@itu.dk
"""

import pytest
import gymnasium as gym
import random
from frozen_lake_agent import FrozenLakeAgent
import csv
import os
import argparse

# Values injected from conftest.py
n_episodes = globals().get("n_episodes", 100)
run_id = globals().get("run_id", 0)
samples = globals().get("samples", 2000)


# Actions
LEFT = 0
DOWN = 1
RIGHT = 2
UP = 3

actions_map = {0: 'LEFT', 1: 'DOWN', 2: 'RIGHT', 3: 'UP'}

@pytest.fixture(scope="session")
def setup():
    # Custom map 4x4:
    #desc=["SFFF", "FFFF", "FHFF", "FFFG"]
    
    # Custom map 7x7:
    desc=["SFFFFFH", "FFFFFFF", "FFHFFFF", "FFFFFFF","HFHFFFF","FFFFFFF","FFFFFFG"]

     # Custom map 9x9:
    #desc=["SFFFFFHFF", "FFFFFFFHF", "FFFFFFFFF", "FHFHFFFFF","FFFFFFFFF","FFFFFFFFF", "FFFFFFFFF", "FFFFFHFFF", "FFFFFFFFG"]

    #env = gym.make('FrozenLake-v1', desc=desc, map_name="4x4", is_slippery=True,render_mode="ansi")
    env = gym.make('FrozenLake-v1', desc=desc, map_name="7x7", is_slippery=True,render_mode="ansi")
   # env = gym.make('FrozenLake-v1', desc=desc, map_name="9x9", is_slippery=True,render_mode="ansi")

    # Positions with holes in 4x4:
    #holes = {9}

    # Positions with holes in 7x7
    holes = {6,16,28,30}

    # Positions with holes in 9x9
    #holes = {6,16,28,30,68}


    # hyperparameters: 
    global learning_rate; learning_rate = 0.1 
    #global n_episodes; n_episodes = 10
    # global n_episodes
    # try:
    #     n_episodes
    # except NameError:
    #     n_episodes = 10
    global start_epsilon; start_epsilon = 0.1
    global epsilon_decay; epsilon_decay = 0
    global final_epsilon; final_epsilon = 0.1
    global seed; seed = 317

    env.action_space.seed(seed)
    random.seed(seed) # random is used only in the training of the agent

    agent = FrozenLakeAgent(
        env,
        learning_rate=learning_rate,
        initial_epsilon=start_epsilon,
        epsilon_decay=epsilon_decay,
        final_epsilon=final_epsilon,
    )

    # Trains the agent using Q-learning with epsilon-greedy
    agent.train(n_episodes,seed)

    print("Number of episodes:",n_episodes)
    policy = agent.get_policy()
   # agent.print_policy()

    steps = 100 # number of steps to test and evaluate the policies on
    eval_steps=100
    print("################")
    print(samples)
    print("################")
    #samples=2000
    # Initialize new environment without seed
    #env = gym.make('FrozenLake-v1', desc=desc, map_name="4x4", is_slippery=True,render_mode="ansi")
    env = gym.make('FrozenLake-v1', desc=desc, map_name="7x7", is_slippery=True,render_mode="ansi")
    #env = gym.make('FrozenLake-v1', desc=desc, map_name="9x9", is_slippery=True,render_mode="ansi")
    evaluate_policy_estimate(policy,env,eval_steps,samples,holes)

    #env = gym.make('FrozenLake-v1', desc=desc, map_name="4x4", is_slippery=True,render_mode="ansi")
    env = gym.make('FrozenLake-v1', desc=desc, map_name="7x7", is_slippery=True,render_mode="ansi")
    #env = gym.make('FrozenLake-v1', desc=desc, map_name="9x9", is_slippery=True,render_mode="ansi")

    evaluate_policy_probtest(policy,env,eval_steps,samples,holes)

    # Initialize new environment without seed
    #env = gym.make('FrozenLake-v1', desc=desc, map_name="4x4", is_slippery=True,render_mode="ansi")
    env = gym.make('FrozenLake-v1', desc=desc, map_name="7x7", is_slippery=True,render_mode="ansi")
    #env = gym.make('FrozenLake-v1', desc=desc, map_name="9x9", is_slippery=True,render_mode="ansi")


    return policy, env, holes, steps

@pytest.fixture()
def policy(setup):
    return setup[0]

@pytest.fixture()
def environment(setup):
    return setup[1]

@pytest.fixture()
def holes(setup):
    return setup[2]

@pytest.fixture()
def steps(setup):
    return setup[3]

def test_never_fall_into_holes(policy,environment,holes,steps):
    """Q1: Given a policy, the agent never falls into a hole in s steps."""

    state, _ = environment.reset()
    for _ in range(steps):
        next_state, reward, terminated, truncated, _  = environment.step(policy.get(state))

        state = next_state

    print(environment.render())
    assert not holes.__contains__(state)

def test_never_takes_too_many_steps(policy,environment,steps):
    """Given a policy, the agent never takes more than s steps before
    reaching a terminal state, i.e., hole or goal state."""

    state, _ = environment.reset()

    for _ in range(steps):
        next_state, reward, terminated, truncated, _  = environment.step(policy.get(state))
        state = next_state

    print(environment.render())
    assert terminated

# #estimation
def evaluate_policy_estimate(policy,environment,steps,samples,holes):
    """ Evaluates the given policy on the probability that Q1 and Q2 does not hold, 
    respectively. Estimates P(neg Q1) and P(neg Q2) for the given policy and number 
    of steps by sampling from the outcome of going on a walk on the environment
    following the policy.
    """

    # Initializes dictionary representing each position in the environment and
    # the number of times we land in each position (updated as we sample)
    estimated_dist = {}
    #change
    #for i in range(16): estimated_dist[i] = 0
    for i in range(49): estimated_dist[i] = 0

    for i in range(samples):
        state, _ = environment.reset()
        for _ in range(steps):
            state, reward, terminated, truncated, _  = environment.step(policy.get(state))

            if terminated or truncated: break
        estimated_dist[state] += 1

    # The probability that we have not fallen into a hole 4x4
   #my_set = {9}

    # The probability that we have not fallen into a hole 7x7
    #my_set = {6,16,28,30}

    # The probability that we have not fallen into a hole 9x9
    #my_set = {6,16,28,30,68}

    prob_neg_q1 = 0.0

    for value in holes:
        print("...........................")
        print(value)
        print("...........................")
        prob_neg_q1 += estimated_dist.get(value, 0) / samples
    print("Neg Q1", "{:.4f}".format(prob_neg_q1))


    #Change
    # The probability that we have not reached a terminal state, i.e., the probability
    # that we do not land in a hole or goal state
    #prob_neg_q2 = 1 - estimated_dist.get(9, 0)/samples - estimated_dist.get(15, 0)/samples

    # The probability that we have not fallen into a hole 4x4
    #my_set = {9}

    # The probability that we have not fallen into a hole 7x7
    #my_set = {6,16,28,30}

    # The probability that we have not fallen into a hole 9x9
    #my_set = {6,16,28,30,68}

    prob_neg_q2 = 0.0

    for value in holes:
      prob_neg_q2+=(-estimated_dist.get(value, 0)/samples)


     #Change
    # The probability that we have not fallen into a hole 4x4
    #prob_neg_q2=1+prob_neg_q2-estimated_dist.get(15, 0)/samples

    # The probability that we have not fallen into a hole 7x7
    # print("**************")
    # print("goal state visit num:")
    # print(-estimated_dist.get(48, 0)/samples)
    # print("falling in the holes num:")
    # print(prob_neg_q2)
    # print("**************")
    prob_neg_q2=1+prob_neg_q2-estimated_dist.get(48, 0)/samples

    # The probability that we have not fallen into a hole 9x9
    #prob_neg_q2=prob_neg_q2-estimated_dist.get(80, 0)/samples

    print("Neg Q2", "{:.4f}".format(prob_neg_q2))
    
    #Change
    #write in csv file
    log_file = f"estimation_results.csv"
    print(f"✅ Saved results to {log_file}")
    write_header = not os.path.exists(log_file)
    with open(log_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["run_id", "samples", "n_episodes","Neg Q1", "Neg Q2"])
        writer.writerow([run_id, samples, n_episodes, round(prob_neg_q1, 4), round(prob_neg_q2, 4)])





#probtest
def evaluate_policy_probtest(policy,environment,steps,samples,holes):
    """ Evaluates the given policy on the probability that Q1 and Q2 does not hold, 
    respectively. Estimates P(neg Q1) and P(neg Q2) for the given policy and number 
    of steps by sampling from the outcome of going on a walk on the environment
    following the policy.
    """

    # Initializes dictionary representing each position in the environment and
    # the number of times we land in each position (updated as we sample)
    estimated_dist = {}
      #change
    #for i in range(16): estimated_dist[i] = 0
    for i in range(49): estimated_dist[i] = 0

    for i in range(299):
        state, _ = environment.reset()
        for _ in range(steps):
            state, reward, terminated, truncated, _  = environment.step(policy.get(state))

            if terminated or truncated: break
        estimated_dist[state] += 1

    # The probability that we have not fallen into a hole
    #prob_neg_q1 = estimated_dist.get(9, 0) / 299

     # The probability that we have not fallen into a hole 4x4
    #my_set = {9}

    # The probability that we have not fallen into a hole 7x7
    #my_set = {6,16,28,30}

    # The probability that we have not fallen into a hole 9x9
    #my_set = {6,16,28,30,68}

    prob_neg_q1 = 0.0

    for value in holes:
        prob_neg_q1 += estimated_dist.get(value, 0) / 299

    bool_neg_q1= 0.0 if prob_neg_q1>0.0 else 1.0
    print("Neg Q1", "{:.4f}".format(prob_neg_q1))

    # Initializes dictionary representing each position in the environment and
    # the number of times we land in each position (updated as we sample)
    estimated_dist = {}
      #change
    #for i in range(16): estimated_dist[i] = 0
    for i in range(49): estimated_dist[i] = 0

    for i in range(2995):
        state, _ = environment.reset()
        for _ in range(steps):
            state, reward, terminated, truncated, _  = environment.step(policy.get(state))

            if terminated or truncated: break
        estimated_dist[state] += 1

    # The probability that we have not reached a terminal state, i.e., the probability
    # that we do not land in a hole or goal state
    # prob_neg_q2 = 1 - estimated_dist.get(9, 0)/2995 - estimated_dist.get(15, 0)/2995
    # print("Neg Q2", "{:.4f}".format(prob_neg_q2))

    # The probability that we have not fallen into a hole 4x4
    #my_set = {9}

    # The probability that we have not fallen into a hole 7x7
    #my_set = {6,16,28,30}

    # The probability that we have not fallen into a hole 9x9
    #my_set = {6,16,28,30,68}

    prob_neg_q2 = 0.0

    for value in holes:
      prob_neg_q2+=(-estimated_dist.get(value, 0)/2995)

    # The probability that we have not fallen into a hole 4x4
    #prob_neg_q2=1+prob_neg_q2-estimated_dist.get(15, 0)/2995

    # The probability that we have not fallen into a hole 7x7
    prob_neg_q2=1+prob_neg_q2-estimated_dist.get(48, 0)/2995

    # The probability that we have not fallen into a hole 9x9
    #prob_neg_q2=1+prob_neg_q2-estimated_dist.get(80, 0)/2995

    bool_neg_q2= 0.0 if prob_neg_q2>0.0 else 1.0

    #write in csv file
    log_file = f"probtest_results.csv"
    print(f"✅ Saved results to {log_file}")
    write_header = not os.path.exists(log_file)

    with open(log_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["run_id", "samples", "n_episodes", "Neg Q1", "Neg Q2", "ProbTest Q1 (holds)", "ProbTest Q2 (holds)"])
        writer.writerow([run_id, samples, n_episodes, round(prob_neg_q1, 4), round(prob_neg_q2, 4), round(bool_neg_q1, 4), round(bool_neg_q2, 4)])


