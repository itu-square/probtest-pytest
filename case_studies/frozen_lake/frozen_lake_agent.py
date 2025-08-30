"""Frozen lake agent trained with Q-learning with epsilon-greedy.

Code based on a tutorial from gymnasium, see
https://gymnasium.farama.org/tutorials/training_agents/blackjack_tutorial/

Copyright: Till Zemann under MIT license.
"""

import gymnasium as gym
import numpy as np
import math
from collections import defaultdict
import random


actions_map = {0: 'LEFT', 1: 'DOWN', 2: 'RIGHT', 3: 'UP'}

class FrozenLakeAgent:
    def __init__(
        self,
        env,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
    ):
        """Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            discount_factor: The discount factor for computing the Q-value
        """
        self.env = env
        self.q_values = defaultdict(lambda: np.zeros(self.env.action_space.n))

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs: tuple[int, int, bool]) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        # with probability epsilon return a random action to explore the environment
        # if np.random.random() < self.epsilon:
        if random.random() < self.epsilon:
            return self.env.action_space.sample()

        # with probability (1 - epsilon) act greedily (exploit)
        else:
            return int(np.argmax(self.q_values[obs]))

    def update(
        self,
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""
        future_q_value = (not terminated) * np.max(self.q_values[next_obs])

        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[obs][action]
        )

        self.q_values[obs][action] = (
            self.q_values[obs][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)
    
    def train(self,n_episodes,seed):
        """Trains the agent for a given number of episodes and with a given seed."""
        outcomes = []
        for i in range(n_episodes):
            obs, info = self.env.reset(seed=seed)
            actions = []
            done = False

            while not done:
                action = self.get_action(obs)
                actions += [action]
                next_obs, reward, terminated, truncated, info  = self.env.step(action)
                #Change
                # #4x4
                # if reward==0: reward=-0.1
                # if not reward==1 and (truncated or terminated) : reward=-1

                # #7x7
                if reward==0: reward=-1
                if not reward==1 and (truncated or terminated) : reward=-60
                
                self.update(obs, action, reward, terminated, next_obs)

                # update if the environment is done and the current obs
                done = terminated or truncated

                obs = next_obs

            outcomes.append(reward)

            self.decay_epsilon()

    def get_policy(self):
        """Returns the policy of the agent, i.e., the action in each state
        with the maximum expected reward."""
        policy = {}
        #Change
        #for i in range(16):
        for i in range(49):
        #for i in range(81):
            policy[i] = int(np.argmax(self.q_values[i]))
        return policy
    
