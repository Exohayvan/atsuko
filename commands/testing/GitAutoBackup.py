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
        
class GitAutoBackup(commands.Cog):
    def __init__(self, bot, private_key_path):
        self.bot = bot
        self.private_key_path = private_key_path
        config = get_config()
        self.github_repo = "Exohayvan/atsuko"
        self.app_id = config.get('APP_ID')
        self.installation_id = config.get('INSTALLATION_ID')
        self.git_dir = os.getcwd()  # Assuming you want the current directory
    
    def get_github_token(self):
        private_key = open(self.private_key_path, 'r').read()
        integration = GithubIntegration(self.app_id, private_key)
        token = integration.get_access_token(self.installation_id)
        return token.token

    def pull_and_push(self):
        token = self.get_github_token()
        remote_url = f"https://x-access-token:{token}@github.com/{self.github_repo}.git"
        
        try:
            subprocess.run(["git", "pull", remote_url], cwd=self.git_dir, check=True)
            subprocess.run(["git", "push", remote_url], cwd=self.git_dir, check=True)
        except subprocess.CalledProcessError:
            print("Error while executing Git commands.")

    # You can invoke this via a command or event as you wish.
    @commands.command(name='backup')
    async def backup_command(self, ctx):
        self.pull_and_push()
        await ctx.send("Backup completed.")
    
async def setup(bot):
    config = get_config()
    private_key_path = config.get('PRIVATE_KEY_PATH')
    await bot.add_cog(GitAutoBackup(bot, private_key_path))
