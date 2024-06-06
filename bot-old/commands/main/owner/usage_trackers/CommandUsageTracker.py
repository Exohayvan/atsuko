import discord
from discord.ext import commands, tasks
import sqlite3
import os

# Import the OwnerCommands cog
# Adjust the import statement according to your project structure.
from commands.main.owner.OwnerCommands import OwnerCommands

class CommandUsageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_listener(self.on_command_completion, "on_command_completion")

    async def on_command_completion(self, ctx):
        # Ignore commands from the OwnerCommands cog
        if isinstance(ctx.command.cog, OwnerCommands):
            return

        command_name = ctx.command.qualified_name
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        conn = sqlite3.connect('./data/command_usage.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS CommandUsage (command_name text, user_id text, guild_id text, usage_count int)')
        
        # Check if there's a record for this command and this user in this guild
        c.execute('SELECT usage_count FROM CommandUsage WHERE command_name = ? AND user_id = ? AND guild_id = ?', (command_name, user_id, guild_id))
        result = c.fetchone()

        if result is None:
            # If not, insert a new record
            c.execute('INSERT INTO CommandUsage VALUES (?, ?, ?, ?)', (command_name, user_id, guild_id, 1))
        else:
            # If yes, increment the usage_count
            c.execute('UPDATE CommandUsage SET usage_count = usage_count + 1 WHERE command_name = ? AND user_id = ? AND guild_id = ?', (command_name, user_id, guild_id))

        conn.commit()
        conn.close()

async def setup(bot):
    await bot.add_cog(CommandUsageTracker(bot))
