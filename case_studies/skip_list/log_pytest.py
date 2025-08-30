import subprocess
import re
import csv
import sys
import logging
import concurrent.futures
import threading

lock = threading.Lock()

if len(sys.argv) != 4:
    print("Usage: python log_pytest.py <num_executions> <bug_prob> <epsilon>")
    logging.error("The input to the script was wrong")
    sys.exit(1)

executions = int(sys.argv[1])
bug_prob = sys.argv[2]
epsilon = sys.argv[3]
R=3
bug=0

# logging config
logging.basicConfig(filename='pytest_log.log', level=logging.INFO, 
                    format=f'%(asctime)s | %(levelname)s | R={R}, bug={bug}, pBug={bug_prob}, epsilon={epsilon} | %(message)s')


def task():
    # Run the pytest command and capture the output
    result = subprocess.run(['pytest', '--probtest', '--Pbug', bug_prob, '--epsilon', epsilon], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Get the output lines
    output_lines = result.stdout.splitlines()

    # Get the last line of the output
    last_line = output_lines[-1] if output_lines else "No output"

    # Print the last line
    with lock:
        logging.info(f"Last line of pytest output: {last_line}")


    # parse last line
    match = re.search(r"(?:(\d+)\s+failed)?(?:,\s*)?(?:(\d+)\s+passed)?\s+in\s+([\d.]+)s", last_line)
    if match:
        failed = match.group(1)
        passed = match.group(2)
        runtime = match.group(3)
    else:
        failed = passed = runtime = "N/A"

    failed = failed if failed != None else 0
    passed = passed if passed != None else 0

    # Define the CSV file name
    csv_file = f'pytest_results_R_{R}_bug_{bug}.csv'

    lock.acquire()
    try:
        # Write the results to the CSV file
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write headers if the file is empty
            if file.tell() == 0:
                writer.writerow(['pBug', 'epsilon', 'failed', 'passed', 'runtime'])
            # Write the parsed results
            writer.writerow([bug_prob, epsilon, failed, passed, runtime])
    finally:
        lock.release()
    
    with lock:
        logging.info(f"Results appended to {csv_file}: failed={failed}, passed={passed}, runtime={runtime}")


# Create a ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # Submit tasks to the thread pool
    futures = [executor.submit(task) for _ in range(executions)]
    
    # Retrieve results as they complete
    counter = 0
    for future in concurrent.futures.as_completed(futures):
        counter += 1
        with lock:
            logging.info(f"Task {counter}/{executions} finished")