import sqlite3
from discord.ext import commands

DATABASE_PATH = "./data/db/disabledcommands.db"

def ensure_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disabled_commands (
        command_name TEXT PRIMARY KEY
    )
    """)
    conn.commit()
    conn.close()

class CommandToggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_database()

    @commands.command(usage="!disable <command_name>")
    async def disable(self, ctx, command_name: str):
        """Disable a specific command."""
        if ctx.author.id == 276782057412362241:
            if command_name in self.bot.all_commands:
                with sqlite3.connect(DATABASE_PATH) as conn:
                    conn.execute("INSERT OR IGNORE INTO disabled_commands (command_name) VALUES (?)", (command_name,))
                await ctx.send(f"`{command_name}` has been disabled!")
            else:
                await ctx.send(f"No command named `{command_name}` found!")
        else:
            await ctx.send("You do not have permission to use this command!")

    @commands.command(usage="!enable <command_name>")
    async def enable(self, ctx, command_name: str):
        """Enable a previously disabled command."""
        if ctx.author.id == 276782057412362241:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM disabled_commands WHERE command_name=?", (command_name,))
                if cursor.rowcount:
                    await ctx.send(f"`{command_name}` has been enabled!")
                else:
                    await ctx.send(f"`{command_name}` is not disabled!")
        else:
            await ctx.send("You do not have permission to use this command!")

async def setup(bot):
    await bot.add_cog(CommandToggle(bot))