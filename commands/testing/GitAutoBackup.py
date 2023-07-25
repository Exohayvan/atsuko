import jwt
import time
import requests
import json
import os
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

GITHUB_BASE_URL = "https://api.github.com"

class GitAutoPushHandler(FileSystemEventHandler):
    def __init__(self, git_dir, get_token_callback):
        self.git_dir = git_dir
        self.get_token_callback = get_token_callback

    def on_modified(self, event):
        if not event.is_directory:
            self.pull_commit_and_push()

    def pull_commit_and_push(self):
        installation_token = self.get_token_callback()

        env = os.environ.copy()
        env["GIT_ASKPASS"] = "echo"
        env["GIT_USERNAME"] = "x-access-token"  # GitHub's convention for using tokens as usernames
        env["GIT_PASSWORD"] = installation_token

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
        with open('../config.json', 'r') as f:
            self.config = json.load(f)

        self.event_handler = GitAutoPushHandler(git_dir=self.path, get_token_callback=self.get_installation_token)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has loaded GitAutoBackup')

    def cog_unload(self):
        self.observer.stop()
        self.observer.join()

    def generate_jwt(self):
        with open(self.config['PRIVATE_KEY_PATH'], 'r') as f:
            private_key = f.read()

        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + (10 * 60),  # 10 minute max expiration
            'iss': self.config['APP_ID']
        }
        return jwt.encode(payload, private_key, algorithm='RS256')

    def get_installation_token(self):
        jwt_token = self.generate_jwt()
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.post(f"{GITHUB_BASE_URL}/app/installations/{self.config['INSTALLATION_ID']}/access_tokens", headers=headers)
        if response.status_code == 201:
            token_data = response.json()
            return token_data['token']
        else:
            return None

async def setup(bot):
    await bot.add_cog(GitAutoBackup(bot))