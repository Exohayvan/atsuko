from discord.ext import commands
import os
import subprocess
import sys
import json
from github import Github

RESTART_EXIT_CODE = 42

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def execute(self, ctx, *, command):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return

        # Execute the command in the terminal
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Send the command output to Discord
        output = result.stdout.strip()
        error = result.stderr.strip()

        if output:
            await ctx.send(f"**Command Output:**\n```{output}```")
        if error:
            await ctx.send(f"**Command Error:**\n```{error}```")
        if not output and not error:
            await ctx.send("The command executed successfully with no output.")

    @commands.command()
    async def tree(self, ctx):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return

        # Get the current directory
        current_dir = os.getcwd()

        # Generate the file list recursively
        file_list = self.generate_file_list(current_dir)

        # Split the file list into chunks of 2000 characters or less
        file_chunks = [file_list[i : i + 2000] for i in range(0, len(file_list), 2000)]

        # Send each chunk of the file list to Discord
        for chunk in file_chunks:
            await ctx.send(f"```{chunk}```")

    def generate_file_list(self, path):
        file_list = []

        # Recursively collect file names in the current directory and subdirectories
        for root, dirs, files in os.walk(path):
            for file_name in files:
                file_list.append(file_name)

        # Return the file names as a newline-separated string
        return '\n'.join(file_list)

    @commands.command()
    async def backup(self, ctx):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return

        # Add changes to git
        result = subprocess.run(["git", "add", "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            await ctx.send(f'Failed to add changes: {result.stderr.decode("utf-8")}')
            return

        # Commit changes
        result = subprocess.run(["git", "commit", "-m", "Backup commit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            await ctx.send(f'Failed to commit changes: {result.stderr.decode("utf-8")}')
            return

        # Push changes
        result = subprocess.run(["git", "push"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            await ctx.send(f'Failed to push changes: {result.stderr.decode("utf-8")}')
            return

        await ctx.send('Backup successful.')
    
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
