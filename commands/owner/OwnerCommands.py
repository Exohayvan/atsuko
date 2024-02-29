from discord.ext import commands
import discord
import os
import subprocess
import sys
import json
from github import Github

RESTART_EXIT_CODE = 42

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def unload_cog(self, ctx, *, cog_path: str):
        # Check if the user has the correct ID
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return
    
        try:
            # Get the cog
            cog = self.bot.get_cog(cog_path.split('.')[-1])
    
            # Check if the cog has a method to stop the subprocess and call it
            if cog and hasattr(cog, "stop_subprocess"):
                cog.stop_subprocess()
    
            # Unload the cog
            await self.bot.unload_extension(f"commands.{cog_path}")
    
            await ctx.send(f'Successfully unloaded cog {cog_path}')
        except commands.ExtensionNotFound:
            await ctx.send(f'Cog {cog_path} not found')
        except Exception as e:
            await ctx.send(f'Error while unloading cog {cog_path}: {str(e)}')
                
    @commands.command(hidden=True)
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

    @commands.command(hidden=True)
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
                    tree_structure += "└── "
                    indent += "    "
                else:
                    tree_structure += "├── "
    
            # Add the item to the tree structure
            tree_structure += f"{item}\n"
    
            # Recursively process subdirectories
            if os.path.isdir(item_path):
                subdirectory_structure = self.generate_tree_structure(item_path, depth + 1, is_last=is_last_item)
    
                # Skip the subdirectory if it doesn't contain any relevant files
                if not subdirectory_structure:
                    continue
    
                # Add the subdirectory structure to the tree structure
                tree_structure += subdirectory_structure
    
        return tree_structure
    
    @discord.app_commands.command(name="update", description="Update the bot's code from the git repository.")
    async def update(self, interaction: discord.Interaction):
        # Correctly check if the user is the bot owner
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        await interaction.response.defer()
        # Perform the git pull operation
        result = subprocess.run(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode("utf-8")
        error = result.stderr.decode("utf-8")

        if "Already up to date." in output:
            await interaction.response.send_message('Already up to date.', ephemeral=True)
            return

        if result.returncode != 0:
            await interaction.followup.send(f'Update failed with error: {error}', ephemeral=True)
        else:
            await interaction.followup.send(f'Update successful: {output}', ephemeral=True)
            await interaction.followup.send('I am restarting.', ephemeral=True)
            sys.exit(RESTART_EXIT_CODE)

    @discord.app_commands.command(name="restart", description="Restart the bot.")
    async def restart(self, interaction: discord.Interaction):
        # Check if the user is the bot owner
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await interaction.response.send_message('I am restarting.', ephemeral=True)
        sys.exit(RESTART_EXIT_CODE)

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))
