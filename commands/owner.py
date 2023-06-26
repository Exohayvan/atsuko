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

        # Generate the tree structure recursively
        tree_structure = self.generate_tree_structure(current_dir)

        # Split the tree structure into lines
        tree_lines = tree_structure.split('\n')

        # Send each line of the tree structure as a separate message
        message = ""
        for line in tree_lines:
            if len(message) + len(line) > 1800:
                await ctx.send("```" + message + "```")
                message = ""
            message += line + '\n'

        if message:
            await ctx.send("```" + message + "```")

    def generate_tree_structure(self, path, depth=0, is_last=False):
        tree_structure = ""
        indent = "  " * depth
    
        # Limit the recursion depth to avoid excessive tree size
        if depth > 4:
            return ""
    
        # Check if the current directory contains any relevant files
        files_in_directory = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        relevant_files_present = any(f.endswith(('.py', '.json', '.db')) and not f.endswith('.pyc') for f in files_in_directory)
    
        # Skip the directory if no relevant files are present
        if not relevant_files_present:
            return ""
    
        # Sort items alphabetically
        items = sorted(os.listdir(path))
    
        # Iterate through all items (files and directories) in the path
        for idx, item in enumerate(items):
            # Get the absolute path of the item
            item_path = os.path.join(path, item)
    
            # Skip directories like "__pycache__"
            if os.path.isdir(item_path) and item.startswith('__'):
                continue
    
            # Check if the item is the last one in the current level
            is_last_item = is_last and idx == len(items) - 1
    
            # Add indentation based on the depth of the item in the directory tree
            tree_structure += f"{indent}"
    
            # Add connecting lines and corners
            if depth > 0:
                if is_last_item:
                    tree_structure += "└─"
                    indent += "  "
                else:
                    tree_structure += "├─"
    
            # Add the item to the tree structure
            tree_structure += f"{item}\n"
    
            # Recursively process subdirectories
            if os.path.isdir(item_path):
                subdirectory_structure = self.generate_tree_structure(item_path, depth + 1, is_last=is_last_item)
    
                # Skip the subdirectory if it doesn't contain any relevant files
                if not subdirectory_structure:
                    continue
    
                # Adjust the subdirectory structure to maintain the desired output format
                subdirectory_structure = subdirectory_structure.replace("  ├─", "  │ ")
                subdirectory_structure = subdirectory_structure.replace("  └─", "    ")
                subdirectory_structure = subdirectory_structure.rstrip()
    
                # Add the subdirectory structure to the tree structure
                tree_structure += subdirectory_structure
    
        return tree_structure

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
