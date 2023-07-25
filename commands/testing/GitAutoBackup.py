import os
import time
import json
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
from github import GithubIntegration, Github

# Retrieving configuration from config.json
def get_config():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    return config

class GitAutoPushHandler(FileSystemEventHandler):
    def __init__(self, git_dir, config):
        self.git_dir = git_dir
        self.config = config

    def on_modified(self, event):
        if not event.is_directory:
            self.pull_commit_and_push()

    def get_github_token(self):
        private_key = open(self.config['PRIVATE_KEY_PATH'], 'r').read()
        integration = GithubIntegration(self.config['APP_ID'], private_key)
        token = integration.get_access_token(self.config['INSTALLATION_ID'])
        return token.token

    def pull_commit_and_push(self):
        token = self.get_github_token()

        env = os.environ.copy()
        env["GIT_ASKPASS"] = "echo"
        env["GIT_USERNAME"] = "x-access-token"
        env["GIT_PASSWORD"] = token

        try:
            subprocess.run(["git", "pull", "origin", "main"], cwd=self.git_dir, env=env, check=True)
            subprocess.run(["git", "add", "."], cwd=self.git_dir, env=env, check=True)
            subprocess.run(["git", "commit", "-m", f"Auto-commit: {time.strftime('%Y-%m-%d %H:%M:%S')}"], cwd=self.git_dir, env=env)
            subprocess.run(["git", "push", "origin", "main"], cwd=self.git_dir, env=env)
        except subprocess.CalledProcessError:
            print("Error while executing Git commands.")

class GitAutoBackup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = os.getcwd()

        # Load the config.json
        self.config = get_config()

        self.event_handler = GitAutoPushHandler(git_dir=self.path, config=self.config)
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
