from discord.ext import commands
import os
import subprocess
import sys
import json
from github import Github

def get_config():
    config_path = "../config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

config = get_config()
GITHUB_TOKEN = config['GITHUB_TOKEN']
GITHUB_REPO = 'https://www.github.com/Exohayvan/astuko'
RESTART_EXIT_CODE = 42

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def update(self, ctx):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return

        # Then, pull the latest code
        result = subprocess.run(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode("utf-8")
        error = result.stderr.decode("utf-8")

        if "Already up to date." in output:
            await ctx.send('Already up to date.')
            return

        if result.returncode != 0:
            await ctx.send(f'Update failed with error: {error}')
        else:
            await ctx.send(f'Update successful: {output}')
            await ctx.send('Bot restarting.')
            sys.exit(RESTART_EXIT_CODE)

    @commands.command()
    async def restart(self, ctx):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return

        await ctx.send('Bot restarting.')
        sys.exit(RESTART_EXIT_CODE)

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))
