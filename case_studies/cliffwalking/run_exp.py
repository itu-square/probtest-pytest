import subprocess
import csv
import os
import time

# === Experiment Parameters ===
n_runs = 100  # Total number of repeated experiments
n_episode_values = range(15000, 30000, 5000)  # Episode values from 10 to 100 inclusive
#samples={200, 300, 1000, 2000, 3000}
samples={2995}


runtime_log = "run_times.csv"
max_retries = 5


write_header = not os.path.exists(runtime_log)
if write_header:
    for attempt in range(max_retries):
        try:
            with open(runtime_log, mode="a", newline="") as logfile:
                writer = csv.writer(logfile)
                writer.writerow(["run_id", "time_seconds"])
            break
        except TimeoutError:
            print(f"Timeout writing header to {runtime_log}, retrying...")
            time.sleep(1)
    else:
        raise TimeoutError("Failed to write header after multiple attempts.")


for run_id in range(n_runs):
    print(f"\n Starting run_id={run_id}")
    start_time = time.time()

    for samplenum in samples:

        for n_episodes in n_episode_values:
            print(f"Running n_episodes={n_episodes}")
            subprocess.run([
                "pytest", "test_cliffwalking.py",
                f"--n-episodes={n_episodes}",
                f"--run-id={run_id}",
                f"--samples={samplenum}",
                "-s"
            ])

        elapsed = round(time.time() - start_time, 2)

        
        for attempt in range(max_retries):
            try:
                with open(runtime_log, mode="a", newline="") as logfile:
                    writer = csv.writer(logfile)
                    writer.writerow([run_id, elapsed])
                break
            except TimeoutError:
                print(f"Timeout writing run {run_id} to {runtime_log}, retrying ({attempt+1}/{max_retries})...")
                time.sleep(1)
        else:
            print(f"Failed to write run {run_id} after multiple attempts.")

        print(f"Completed run_id={run_id} in {elapsed} seconds")

print("\nAll runs completed. Timing data saved to run_times.csv")
