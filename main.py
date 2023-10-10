import os
import discord
from discord.ext import commands
import json
import logging
import asyncio
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
    
        categories = {}
    
        for cog, commands in mapping.items():
            if not commands:
                continue
    
            if cog is None:
                cog_name = "Other"
            else:
                cog_path = cog.__module__.split('.')
                if len(cog_path) > 2:
                    # Use directory name as category title if the command is in a subdirectory
                    cog_name = cog_path[-2].capitalize()
                else:
                    # Use "Other" as category title if the command is in the root directory
                    cog_name = "Other"
    
            if cog_name not in categories:
                categories[cog_name] = []
    
            categories[cog_name].extend([command.name for command in commands if not command.hidden])
    
        for category, commands in categories.items():
            commands_list = ', '.join(commands)
    
            if commands_list:
                embed.add_field(name=category, value=commands_list, inline=False)
    
        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        prefix = await self.get_prefix(self.context.bot, self.context.message)
        embed = discord.Embed(title=f'{prefix}{command.name}', description=command.help or "No description provided", color=discord.Color.blue())
        embed.add_field(name="Usage", value=f'{prefix}{command.name} {command.signature}', inline=False)

        await self.context.send(embed=embed)

intents = discord.Intents.all()

async def determine_prefix(bot, message):
    if message.guild is None:  # Check if the message is from a DM
        return '!' 
    conn = sqlite3.connect('./data/prefix.db')
    cursor = conn.cursor()
    cursor.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (message.guild.id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        prefix = result[0]
    else:
        prefix = '!'

    return commands.when_mentioned_or(prefix)(bot, message)

bot = commands.Bot(command_prefix=determine_prefix, intents=intents)
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
    conn.close()
    
def initialize_tos_database():
    conn = sqlite3.connect('./data/tos.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tos_accepted (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

async def has_accepted_tos(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('./data/tos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM tos_accepted WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return True
    else:
        await ctx.send("You need to accept our Terms of Service before using this command. Please visit https://github.com/Exohayvan/atsuko/blob/main/TOS.md to read it then use `!accept_tos` accept it.")
        return False

bot.add_check(has_accepted_tos)

@bot.command(name="accept_tos")
async def accept_tos(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('./data/tos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO tos_accepted (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    await ctx.send("Thank you for accepting the Terms of Service!")
    
async def load_cogs(bot, root_dir):
    tasks = []
    num_cogs = 0
    
    # Load all cogs except those in commands/docs
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "commands/docs" in dirpath:  # skip this directory for now
            continue
        for filename in filenames:
            if filename.endswith('.py'):
                await handle_loading(dirpath, filename, bot, tasks)
                num_cogs += 1

    # Now, load cogs in commands/docs directory
    for dirpath, dirnames, filenames in os.walk(os.path.join(root_dir, 'docs')):
        for filename in filenames:
            if filename.endswith('.py'):
                await handle_loading(dirpath, filename, bot, tasks)
                num_cogs += 1

    await asyncio.gather(*tasks)
    return num_cogs

async def handle_loading(dirpath, filename, bot, tasks):
    path = os.path.join(dirpath, filename)
    module = path.replace(os.sep, ".")[:-3]
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

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    channel = None
    # Check if restart_id.temp exists
    if os.path.exists('restart_id.temp'):
        with open('restart_id.temp', 'r') as f:
            data = json.load(f)
            channel_id = data.get('channel_id')
        
        if channel_id:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send("I am starting back up!")
        
        # Remove the file after reading it
        os.remove('restart_id.temp')

    # Always load command cogs, regardless of whether restart_id.temp exists or not
    num_cogs = await load_cogs(bot, 'commands')
    
    if channel:
        await channel.send(f"Cogs loaded ({num_cogs} cogs)")
        await channel.send("I have restarted!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

initialize_database()
initialize_tos_database()

config = get_config()
bot.run(config['bot_token'])