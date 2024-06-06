from discord.ext import commands, tasks
from discord import Game, Activity, ActivityType
import itertools

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.statuses = itertools.cycle([
            ("with the !help command 📚", ActivityType.playing),  
            (f"{len(self.bot.users)} users 👥", ActivityType.watching),
            (f"{len(self.bot.guilds)} servers 🌐", ActivityType.watching),
            (f"{sum(len(guild.channels) for guild in self.bot.guilds)} channels 💬", ActivityType.watching),
            ("my creator, ExoHayvan 🩵", ActivityType.listening)
        ])
        self.change_presence.start()  # Start the task

    def cog_unload(self):
        self.change_presence.cancel()  # Cancel the task when the cog gets unloaded

    @tasks.loop(seconds=15)
    async def change_presence(self):
        """Automatically changes the bot's presence every 15 seconds."""
        next_status, activity_type = next(self.statuses)
        activity = Activity(name=next_status, type=activity_type)
        await self.bot.change_presence(activity=activity)

    @change_presence.before_loop
    async def before_change_presence(self):
        await self.bot.wait_until_ready()  # Wait until the bot has connected to discord

async def setup(bot):
    await bot.add_cog(Presence(bot))
