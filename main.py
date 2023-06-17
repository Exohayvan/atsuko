import os
import discord
from discord.ext import commands
import json
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
        
        for cog, commands in mapping.items():
            if not commands:
                continue  # Ignore empty cogs/uncategorized commands

            cog_name = getattr(cog, "qualified_name", "No Category")
            commands_list = ', '.join([command.name for command in commands if not command.hidden])

            if commands_list:
                embed.add_field(name=cog_name, value=commands_list, inline=False)

        await self.context.send(embed=embed)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.help_command = CustomHelpCommand()

def get_config():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    return config

async def load_cogs(bot, root_dir):
    tasks = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(dirpath, filename)
                module = path.replace(os.sep, ".")[:-3]  # replace path separators with '.' and remove '.py'
                tasks.append(bot.load_extension(module))
                print(f"Loaded Command: {filename[:-3]}")
            else:
                print("Unable to load pycache folder.")

    await asyncio.gather(*tasks)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await load_cogs(bot, 'Commands')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f'An error occurred: {str(error)}')

config = get_config()
bot.run(config['bot_token'])
