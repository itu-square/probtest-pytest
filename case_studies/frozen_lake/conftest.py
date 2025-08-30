import pytest
import sys
import importlib.util
from pathlib import Path

def pytest_addoption(parser):
    parser.addoption(
        "--n-episodes", action="store", default=100, type=int,
        help="Number of training episodes"
    )
    parser.addoption(
        "--run-id", action="store", default=0, type=int,
        help="Unique run ID for experiment tracking"
    )

    parser.addoption(
        "--samples", action="store", default=0, type=int,
        help="Sample numbers for experiment tracking"
    )

def pytest_configure(config):
    # Get command-line arguments
    n_episodes = config.getoption("--n-episodes")
    run_id = config.getoption("--run-id")
    samples = config.getoption("--samples")

    # Dynamically import test_frozen_lake.py
    test_path = Path(__file__).parent / "test_frozen_lake.py"
    spec = importlib.util.spec_from_file_location("test_frozen_lake", str(test_path))
    test_mod = importlib.util.module_from_spec(spec)
    sys.modules["test_frozen_lake"] = test_mod
    spec.loader.exec_module(test_mod)

    # Inject values before pytest collects tests
    setattr(test_mod, "n_episodes", n_episodes)
    setattr(test_mod, "run_id", run_id)
    setattr(test_mod, "samples", samples)
