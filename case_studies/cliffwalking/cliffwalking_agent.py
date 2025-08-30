import gymnasium as gym
import numpy as np

class CliffWalkingAgent:
    def __init__(self, env_id="CustomCliffWalking-v1", learning_rate=0.1, epsilon=0.2,
                 gamma=0.99, seed=42):
        self.env_id = env_id
        self.epsilon = epsilon
        self.gamma = gamma
        self.lr = learning_rate
        self.seed = seed

        # Environment for training (with seed for reproducibility)
        self.env = gym.make(env_id)
        self.env.reset(seed=seed)

        # Q-table initialization
        self.q_table = np.zeros((self.env.observation_space.n, self.env.action_space.n))

    def train(self, n_episodes):
        for episode in range(n_episodes):
            state, _ = self.env.reset(seed=self.seed)
            done = False

            while not done:
                # Epsilon-greedy action selection
                if np.random.rand() < self.epsilon:
                    action = self.env.action_space.sample()
                else:
                    action = np.argmax(self.q_table[state])

                next_state, reward, terminated, truncated, _ = self.env.step(action)
                done = terminated or truncated

                # Q-learning update
                td_target = reward + self.gamma * np.max(self.q_table[next_state])
                td_error = td_target - self.q_table[state, action]
                self.q_table[state, action] += self.lr * td_error

                state = next_state

        # Decay epsilon after each episode
        self.epsilon = max(0.01, self.epsilon * 0.995)


    def get_policy(self):
        """Returns a deterministic policy as a dictionary: state -> best action."""
        return {s: int(np.argmax(a)) for s, a in enumerate(self.q_table)}

    def get_policy_function(self, epsilon=0.0):
        """Returns an epsilon-greedy policy function for evaluation."""
        def policy(state):
            if np.random.rand() < epsilon:
                return self.env.action_space.sample()
            return int(np.argmax(self.q_table[state]))
        return policy



# import gymnasium as gym
# import numpy as np

# class CliffWalkingAgent:
#     # def __init__(self, env_id="CustomCliffWalking-v1", learning_rate=0.1, epsilon=0.1,
#     #              gamma=0.99, seed=42):
#     def __init__(self, env_id="CustomCliffWalking-v1", learning_rate=0.1, epsilon=0.1,
#                  gamma=0.99):
#         self.env_id = env_id
#         #self.seed = seed
#         self.epsilon = epsilon
#         self.gamma = gamma
#         self.lr = learning_rate

#         self.env = gym.make(env_id)
#        # self.env.reset(seed=seed)
#         self.env.reset()

#         self.q_table = np.zeros((self.env.observation_space.n, self.env.action_space.n))

#     def train(self, n_episodes):
#         for episode in range(n_episodes):
#             state, _ = self.env.reset()
#             done = False
#             while not done:
#                 if np.random.rand() < self.epsilon:
#                     action = self.env.action_space.sample()
#                 else:
#                     action = np.argmax(self.q_table[state])

#                 next_state, reward, terminated, truncated, _ = self.env.step(action)
#                 done = terminated or truncated

#                 td_target = reward + self.gamma * np.max(self.q_table[next_state])
#                 td_error = td_target - self.q_table[state, action]
#                 self.q_table[state, action] += self.lr * td_error

#                 state = next_state

#     def get_policy(self):
#         """Returns a greedy policy (dict from state to best action)."""
#         return {s: int(np.argmax(a)) for s, a in enumerate(self.q_table)}

#     def get_policy_function(self, epsilon=0.0):
#         """Returns a callable epsilon-greedy policy function."""
#         def policy(state):
#             if np.random.rand() < epsilon:
#                 return self.env.action_space.sample()
#             return int(np.argmax(self.q_table[state]))
#         return policy
