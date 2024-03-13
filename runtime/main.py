import json
import subprocess
from time import sleep

import os
script_path = os.path.abspath(__file__)
directory_path = os.path.dirname(script_path)
os.chdir(directory_path)

scripts = {
    "bot": "../bot/app.py",
    "web": "web.app:app"
}
processes = {}

def read_config():
    with open('run.json', 'r') as file:
        return json.load(file)

def manage_scripts():
    config = read_config()

    for script, should_run in config.items():
        if should_run:
            if script not in processes or processes[script].poll() is not None:
                print(f"Starting {script}...")
                if script == "web":
                    command = ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", scripts[script]]
                    processes[script] = subprocess.Popen(command, cwd="/atsuko")
                else:
                    processes[script] = subprocess.Popen(['python3', scripts[script]])
        else:
            if script in processes:
                print(f"Stopping {script}...")
                processes[script].kill()

if __name__ == "__main__":
    while True:
        manage_scripts()
        sleep(10)
