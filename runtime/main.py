import json
import subprocess
from time import sleep

scripts = {
    "bot": "../bot/app.py",
    "web": "../web/app.py"
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
                processes[script] = subprocess.Popen(['python', scripts[script]])
        else:
            if script in processes:
                print(f"Stopping {script}...")
                processes[script].kill()

if __name__ == "__main__":
    while True:
        manage_scripts()
        sleep(10)
