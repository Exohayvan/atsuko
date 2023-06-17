# watcher.py
import subprocess

RESTART_EXIT_CODE = 42  # or any number you choose

while True:
    process = subprocess.Popen(["python3", "main.py"])
    exit_code = process.wait()
    if exit_code != RESTART_EXIT_CODE:
        break
