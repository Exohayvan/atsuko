from discord.ext import commands
import datetime

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = self.load_start_time()

    def load_start_time(self):
        try:
            with open("start_time.txt", "r") as f:
                start_time_str = f.read()
                return datetime.datetime.fromisoformat(start_time_str)
        except FileNotFoundError:
            return datetime.datetime.utcnow()

    def save_start_time(self):
        with open("start_time.txt", "w") as f:
            start_time_str = self.start_time.isoformat()
            f.write(start_time_str)

    @commands.Cog.listener()
    async def on_ready(self):
        self.start_time = self.load_start_time()

    @commands.command()
    async def uptime(self, ctx):
        """Shows the current uptime of the bot."""
        delta = datetime.datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        await ctx.send(f"Current Uptime: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds.")

    @commands.command()
    async def lifetime(self, ctx):
        """Shows the total lifetime uptime of the bot."""
        now = datetime.datetime.utcnow()
        delta = now - self.start_time
        days, seconds = delta.days, delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        await ctx.send(f"Total Lifetime Uptime: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds.")

    def cog_unload(self):
        self.save_start_time()

async def setup(bot):
    await bot.add_cog(Info(bot))
