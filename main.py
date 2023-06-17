import os
import discord
from discord.ext import commands
import json

class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f'{self.context.prefix}{command.qualified_name} {command.signature}'

    async def send_bot_help(self, mapping):
        for cog, commands in mapping.items():
            if cog:
                await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in commands]}')

    async def send_cog_help(self, cog):
        await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in cog.get_commands()]}')

    async def send_command_help(self, command):
        await self.get_destination().send(f'{self.get_command_signature(command)}\n{command.help}')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.help_command = CustomHelpCommand()

def get_config():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    return config

@bot.event
async def on_ready():
    for dirpath, dirnames, filenames in os.walk('./Commands'):
        for filename in filenames:
            if filename.endswith('.py'):
                await bot.load_extension(f'{dirpath.replace("/",".")}.{filename[:-3]}')
                print(f"Loaded Command: {filename[:-3]}")
            else:
                print("Unable to load pycache folder.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f'An error occurred: {str(error)}')

config = get_config()
bot.run(config['bot_token'])
