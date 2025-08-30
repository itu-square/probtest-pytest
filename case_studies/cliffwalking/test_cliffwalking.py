import pytest
import gymnasium as gym
from gymnasium.envs.registration import register, registry
import os
import csv

from cliffwalking_agent import CliffWalkingAgent
from cliffwalking_env import CliffWalkingEnv  


n_episodes = globals().get("n_episodes", 100)
run_id = globals().get("run_id", 0)
samples = globals().get("samples", 2000)

@pytest.fixture(scope="session")
def setup():
   
    if "CustomCliffWalking-v1" not in registry:
        register(
            id="CustomCliffWalking-v1",
            entry_point="cliffwalking_env:CliffWalkingEnv",
            max_episode_steps=100,
            kwargs={"is_slippery": True}
        )

    env_id = "CustomCliffWalking-v1"
    safe_steps = 30

    # Train with seeded env
    train_env = gym.make(env_id)
    agent = CliffWalkingAgent(env_id=env_id)
    agent.train(n_episodes)


    policy = agent.get_policy_function(epsilon=0.0)


    eval_env = gym.make(env_id)

    # Run evaluations
    evaluate_policy_estimation(policy, eval_env, samples, safe_steps)
    eval_env = gym.make(env_id)
    evaluate_policy_probtest(policy, eval_env, samples, safe_steps)
    eval_env = gym.make(env_id)

    return policy, eval_env, safe_steps


@pytest.fixture
def policy(setup):
    return setup[0]

@pytest.fixture
def environment(setup):
    return setup[1]

@pytest.fixture
def safe_steps(setup):
    return setup[2]


def test_does_not_fall_off_cliff(policy, environment, safe_steps):
    state, _ = environment.reset()
    for step in range(safe_steps):
        action = policy(state)
        next_state, reward, terminated, truncated, _ = environment.step(action)

        if reward == -100:
            raise AssertionError(f"💥 Agent fell off cliff and got reset at step {step}!")

        state = next_state
        if terminated or truncated:
            break


def evaluate_policy_estimation(policy, env, samples, safe_steps):
    """Estimate P(¬Q1): probability agent falls into cliff within `safe_steps`."""
    count_cliff = 0
    for _ in range(samples):
        state, _ = env.reset()
        for _ in range(safe_steps):
            next_state, reward, terminated, truncated, _ = env.step(policy(state))
            if reward == -100:
                count_cliff += 1
                break
            state = next_state

    prob_neg_q = count_cliff / samples
    log_results("estimation_results.csv", ["run_id", "samples", "n_episodes", "Neg Q"],
                [run_id, samples, n_episodes, round(prob_neg_q, 4)])


def evaluate_policy_probtest(policy, env, samples, safe_steps):
    """Binary test for whether P(¬Q1) ≤ 0.01."""
    samples = 2995
    count_cliff = 0
    for _ in range(samples):
        state, _ = env.reset()
        for _ in range(safe_steps):
            next_state, reward, terminated, truncated, _ = env.step(policy(state))
            if reward == -100:
                count_cliff += 1
                break
            state = next_state

    prob_neg_q = count_cliff / samples
    bool_neg_q = 0.0 if prob_neg_q > 0.0 else 1.0

    log_results("probtest_results.csv",
                ["run_id", "samples", "n_episodes", "Neg Q", "probtest Q"],
                [run_id, samples, n_episodes, round(prob_neg_q, 4), bool_neg_q])


def log_results(filename, headers, values):
    write_header = not os.path.exists(filename)
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(headers)
        writer.writerow(values)
    print(f"Saved results to {filename}")



