from discord.ext import commands, tasks
from discord import Game, ActivityType
import itertools

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_presence.start()  # Start the task

    def cog_unload(self):
        self.change_presence.cancel()  # Cancel the task when the cog gets unloaded

    @tasks.loop(seconds=30)
    async def change_presence(self):
        """Automatically changes the bot's presence every 30 seconds."""
        statuses = [
            "with the !help command 📚",  
            f"with {len(self.bot.users)} users 👥",
            f"on {len(self.bot.guilds)} servers 🌐",
            f"around {sum(len(guild.channels) for guild in self.bot.guilds)} channels 💬",
            "with my creator, ExoHayvan 🩵"
        ]
        self.statuses = itertools.cycle(statuses)
        next_status = next(self.statuses)
        await self.bot.change_presence(activity=Game(name=next_status))
        print(f'Presence changed to: {next_status}')

    @change_presence.before_loop
    async def before_change_presence(self):
        await self.bot.wait_until_ready()  # Wait until the bot has connected to discord

async def setup(bot):
    await bot.add_cog(Presence(bot))
