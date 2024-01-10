import os
import discord
from discord.ext import commands
import json
import logging
import asyncio
import sqlite3

logging.basicConfig(level=logging.INFO)

# Global variable for TOS message ID
tos_message_id = None
pending_commands = {}  # user_id: ctx

class CustomHelpCommand(commands.HelpCommand):
    async def get_prefix(self, bot, message):
        if message.guild is None:  # If the message is a DM
            return '!'  # Return the default prefix or handle as needed
    
        conn = sqlite3.connect('./data/prefix.db')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (message.guild.id,))
            result = cursor.fetchone()
        finally:
            conn.close()
    
        if result and result[0]:
            return result[0]
        else:
            return '!'  # Return the default prefix if no specific prefix is set for the guild

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

bot = commands.Bot(command_prefix=determine_prefix, intents=intents, case_insensitive=True)
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
    global tos_message_id
    global pending_commands
    if ctx.command.name == "accept_tos":
        return True
        
    user_id = ctx.author.id

    conn = sqlite3.connect('./data/tos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM tos_accepted WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return True
    else:
        embed = discord.Embed(title="Terms of Service", description="You need to accept our Terms of Service before using this command.", color=discord.Color.red())
        embed.add_field(name="Read the TOS", value="[Click here to read the TOS](https://github.com/Exohayvan/atsuko/blob/main/documents/TOS.md)", inline=False)
        embed.add_field(name="Accept the TOS", value="React with ✅ or use `!accept_tos` to accept the Terms of Service.", inline=False)
        tos_message = await ctx.send(embed=embed)
        await tos_message.add_reaction('✅')
        tos_message_id = tos_message.id

        pending_commands[user_id] = ctx

        # Schedule TOS message deletion after 60 seconds
        await asyncio.sleep(60)
        await tos_message.delete()

        return False
        
bot.add_check(has_accepted_tos)

def is_command_disabled(command_name):
    conn = sqlite3.connect('./data/db/disabledcommands.db')
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM disabled_commands WHERE command_name = ?", (command_name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

async def check_if_command_disabled(ctx):
    command_name = ctx.command.name
    if is_command_disabled(command_name):
        response_message = (
            f"The `{command_name}` command is currently disabled. "
            "This could be due to a few reasons:\n"
            "- The command might be undergoing updates or maintenance.\n"
            "- There could be an identified issue or error that's being fixed.\n"
            "- It might be temporarily disabled to improve server performance.\n\n"
            "If you believe this is an error, or if you have any concerns, "
            "please message ExoHayvan on Discord for assistance."
        )
        await ctx.send(response_message)
        return False
    return True

bot.add_check(check_if_command_disabled)

@bot.command(name="tos_stats")
async def tos_stats(ctx):
    # Step 1: Count total number of unique users the bot can see
    total_users = set()  # Using a set to avoid counting duplicates
    for guild in bot.guilds:
        for member in guild.members:
            total_users.add(member.id)
    total_count = len(total_users)

    # Step 2: Count users who've accepted the TOS
    conn = sqlite3.connect('./data/tos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(user_id) FROM tos_accepted")
    accepted_count = cursor.fetchone()[0]
    conn.close()

    # Step 3: Compute the percentage
    if total_count > 0:
        accepted_percentage = (accepted_count / total_count) * 100
    else:
        accepted_percentage = 0

    # Send the stats
    embed = discord.Embed(title="TOS Acceptance Statistics", color=discord.Color.blue())
    embed.add_field(name="Total Users", value=str(total_count), inline=True)
    embed.add_field(name="Accepted TOS", value=str(accepted_count), inline=True)
    embed.add_field(name="Percentage Accepted", value=f"{accepted_percentage:.5f}%", inline=True)
    await ctx.send(embed=embed)
    
@bot.command(name="accept_tos")
async def accept_tos(ctx):
    await accept_tos_procedure(ctx.author)
    await ctx.send("Thank you for accepting the Terms of Service!", delete_after=60)
    await asyncio.sleep(60)
    await ctx.message.delete()
            
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
        
        await channel.send("Loading cogs...")
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
    
@bot.event
async def on_reaction_add(reaction, user):
    global tos_message_id
    if user.bot or str(reaction.emoji) != '✅':
        return

    if reaction.message.id == tos_message_id:
        await accept_tos_procedure(user)

async def accept_tos_procedure(user):
    global pending_commands
    user_id = user.id

    conn = sqlite3.connect('./data/tos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO tos_accepted (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    if user_id in pending_commands:
        ctx = pending_commands[user_id]
        await bot.invoke(ctx)
        del pending_commands[user_id]

initialize_database()
initialize_tos_database()

config = get_config()
bot.run(config['bot_token'])