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

    async def send_command_help(self, command):
        await self.get_destination().send(f'{self.get_command_signature(command)}\n{command.help}')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.help_command = CustomHelpCommand()

def get_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

def load_cogs(bot, root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(dirpath, filename)
                module = path.replace(os.sep, ".")[:-3]  # replace path separators with '.' and remove '.py'
                bot.load_extension(module)

load_cogs(bot, 'Commands')

config = get_config()
bot.run(config['bot_token'])
