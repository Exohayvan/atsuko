import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class GitAutoPushHandler(FileSystemEventHandler):
    def __init__(self, git_dir):
        self.git_dir = git_dir

    def on_modified(self, event):
        if not event.is_directory:
            self.pull_commit_and_push()

    def pull_commit_and_push(self):
        try:
            # Pull the latest changes
            subprocess.run(["git", "pull", "origin", "main"], cwd=self.git_dir, check=True)

            # Commit local changes
            subprocess.run(["git", "add", "."], cwd=self.git_dir, check=True)
            subprocess.run(["git", "commit", "-m", f"Auto-commit: {time.strftime('%Y-%m-%d %H:%M:%S')}"], cwd=self.git_dir)

            # Push changes to the remote repository
            subprocess.run(["git", "push", "origin", "main"], cwd=self.git_dir)
        except subprocess.CalledProcessError:
            print("Error while executing Git commands.")

if __name__ == "__main__":
    path = os.getcwd()  # Gets the current directory
    event_handler = GitAutoPushHandler(git_dir=path)

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(60)  # Check every 60 seconds
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
