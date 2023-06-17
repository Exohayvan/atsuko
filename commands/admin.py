from discord.ext import commands
import os
import subprocess
import sys
import json

def get_config():
    config_path = "../config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

config = get_config()
GITHUB_TOKEN = config['GITHUB_TOKEN']
GITHUB_REPO = 'https://github.com/Exohayvan/astuko'
RESTART_EXIT_CODE = 42

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def update(self, ctx):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return

        # Initialize a GitHub API object using your token
        g = Github(GITHUB_TOKEN)

        # Get the repository
        repo = g.get_repo(GITHUB_REPO)

        # Get the name of the latest commit
        latest_commit = repo.get_commits()[0].sha

        # Check if the latest commit is the currently running code
        if os.environ.get('CURRENT_COMMIT') != latest_commit:
            # If not, update the repository URL with the GitHub token
            repo_url = GITHUB_REPO
            new_repo_url = repo_url.replace("https://", f"https://{GITHUB_TOKEN}@github.com/")
            subprocess.run(["git", "remote", "set-url", "origin", new_repo_url], check=True)

            # Then, pull the latest code and update the environment variable
            result = subprocess.run(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode("utf-8")
            error = result.stderr.decode("utf-8")
            os.environ['CURRENT_COMMIT'] = latest_commit
            if error:
                await ctx.send(f'Update failed with error: {error}')
            else:
                await ctx.send(f'Update successful: {output}')
                await ctx.send('Bot restarting.')
                sys.exit(RESTART_EXIT_CODE)
        else:
            await ctx.send('Already up to date.')

    @commands.command()
    async def restart(self, ctx):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return

        await ctx.send('Bot restarting.')
        sys.exit(RESTART_EXIT_CODE)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
