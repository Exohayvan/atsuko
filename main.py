import os
import discord
from discord.ext import commands
import json
import logging
import asyncio
import random
import sqlite3

logging.basicConfig(level=logging.INFO)

class CustomHelpCommand(commands.HelpCommand):
    async def get_prefix(self, bot, message):
        conn = sqlite3.connect('./data/prefix.db')
        cursor = conn.cursor()
        cursor.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (message.guild.id,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return result[0]
        return '!'

    async def send_bot_help(self, mapping):
        prefix = await self.get_prefix(self.context.bot, self.context.message)
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
        embed.set_footer(text=f"Prefix: {prefix}")

        for cog, commands in mapping.items():
            if not commands:
                continue

            cog_name = getattr(cog, "qualified_name", "No Category")
            commands_list = ', '.join([command.name for command in commands if not command.hidden])

            if commands_list:
                embed.add_field(name=cog_name, value=commands_list, inline=False)

        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        prefix = await self.get_prefix(self.context.bot, self.context.message)
        embed = discord.Embed(title=f'{prefix}{command.name}', description=command.help or "No description provided", color=discord.Color.blue())
        embed.add_field(name="Usage", value=f'{prefix}{command.name} {command.signature}', inline=False)

        await self.context.send(embed=embed)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=None, intents=intents)  # Set initial prefix to None
bot.help_command = CustomHelpCommand()

def get_config():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    return config

def initialize_database():
    conn = sqlite3.connect('./data/prefix.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id INTEGER PRIMARY KEY, prefix TEXT)")
    conn.commit()
    return conn

async def load_cogs(bot, root_dir):
    tasks = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(dirpath, filename)
                module = path.replace(os.sep, ".")[:-3]  # replace path separators with '.' and remove '.py'
                cog = module.replace(".", "_")
                try:
                    task = asyncio.create_task(bot.load_extension(module))
                    tasks.append(task)
                    print(f"Loaded Cog: {module}")
                except Exception as e:
                    print(f"Failed to load Cog: {module}\n{e}")
                try:
                    setup = getattr(bot.get_cog(cog), "setup")
                    if setup:
                        tasks.append(asyncio.create_task(setup(bot)))
                except AttributeError:
                    pass

    await asyncio.gather(*tasks)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    user_count = sum(guild.member_count for guild in bot.guilds)
    await bot.change_presence(activity=discord.Game(name=f"!help with {user_count} users"))
    await load_cogs(bot, 'commands')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    if message.content.lower() == 'ratio':
        roast_messages = [
            "Your ratio is like dividing by zero. It doesn't make any sense.",
            "Who needs a calculator when we have your ratio? It's always wrong.",
            "Your ratio is so bad, it's a wonder you even try.",
            "Congratulations, your ratio is the square root of negative one. Imaginary and useless.",
            "Your ratio is the reason why mathematicians get headaches.",
            "Step aside, everyone! We've got a ratio expert here. Just kidding, you're terrible at it.",
            "Your ratio is like a broken pencil. Pointless.",
            "I thought I've seen bad ratios, but yours takes the cake. And throws it away.",
            "Your ratio is so bad, it's beyond redemption. Just like your taste in jokes.",
            "Ratio? More like a sad attempt to feel important.",
            "Your ratio is like a black hole. Everything gets sucked into its emptiness.",
            "Did you know your ratio has its own fan club? Just kidding, no one likes it.",
            "I've seen better ratios on a preschooler's finger paintings.",
            "Your ratio is like dividing by potato. It makes no sense.",
            "Your ratio is the mathematical equivalent of a horror movie.",
            "Don't worry, your ratio is safe with me. No one else would want it anyway.",
            "Your ratio is so bad, it's a wonder you're even allowed near numbers.",
            "Is your ratio trying to break a record for being the worst? Because it's doing a great job.",
            "Your ratio is like a glitch in the matrix. It defies all logic.",
            "I've heard legends of bad ratios, but yours surpasses them all.",
        ]
        response = random.choice(roast_messages)
        await message.channel.send(response)

    # Get the command prefix using the CustomHelpCommand's get_prefix method
    prefix = await bot.help_command.get_prefix(bot, message)
    bot.command_prefix = prefix  # Set the command prefix for the bot

    await bot.process_commands(message)

initialize_database()

config = get_config()
bot.run(config['bot_token'])
