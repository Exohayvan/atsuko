import os
import time
from discord.ext import commands
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
            subprocess.run(["git", "pull", "origin", "main"], cwd=self.git_dir, check=True)
            subprocess.run(["git", "add", "."], cwd=self.git_dir, check=True)
            subprocess.run(["git", "commit", "-m", f"Auto-commit: {time.strftime('%Y-%m-%d %H:%M:%S')}"], cwd=self.git_dir)
            subprocess.run(["git", "push", "origin", "main"], cwd=self.git_dir)
        except subprocess.CalledProcessError:
            print("Error while executing Git commands.")

class GitAutoBackup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = os.getcwd()
        self.event_handler = GitAutoPushHandler(git_dir=self.path)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has loaded GitAutoBackup')

    def cog_unload(self):
        self.observer.stop()
        self.observer.join()

async def setup(bot):
    await bot.add_cog(GitAutoBackup(bot))
