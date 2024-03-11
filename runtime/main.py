import json
import subprocess
from time import sleep

# Paths to your scripts
scripts = {
    "script1": "path/to/script1.py",
    "script2": "path/to/script2.py"
}

# Process handles
processes = {}

def read_config():
    with open('config.json', 'r') as file:
        return json.load(file)

def manage_scripts():
    config = read_config()

    for script, should_run in config.items():
        if should_run:
            if script not in processes or processes[script].poll() is not None:
                # Start or restart the script
                print(f"Starting {script}...")
                processes[script] = subprocess.Popen(['python', scripts[script]])
        else:
            if script in processes:
                # Stop the script
                print(f"Stopping {script}...")
                processes[script].kill()

if __name__ == "__main__":
    while True:
        manage_scripts()
        sleep(10)  # Check every 10 seconds
