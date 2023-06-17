from discord.ext import commands
import datetime

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime_start = datetime.datetime.utcnow()  # The uptime should start from the moment of the latest bot's initialization
        self.lifetime_start = self.load_lifetime_start()

    def load_lifetime_start(self):
        try:
            with open("start_time.txt", "r") as f:
                start_time_str = f.read()
                return datetime.datetime.fromisoformat(start_time_str)
        except FileNotFoundError:
            # If the file doesn't exist, that means it's the bot's first boot. 
            # Therefore, we save the current boot time as the lifetime start.
            self.save_lifetime_start()
            return datetime.datetime.utcnow()

    def save_lifetime_start(self):
        with open("start_time.txt", "w") as f:
            lifetime_start_str = self.lifetime_start.isoformat()
            f.write(lifetime_start_str)

    @commands.Cog.listener()
    async def on_ready(self):
        # When the bot is ready, update the uptime start.
        self.uptime_start = datetime.datetime.utcnow()

    @commands.command()
    async def uptime(self, ctx):
        """Shows the current uptime of the bot since last reboot."""
        delta = datetime.datetime.utcnow() - self.uptime_start
        await self.send_uptime_message(ctx, "Current Uptime", delta)

    @commands.command()
    async def lifetime(self, ctx):
        """Shows the total lifetime uptime of the bot."""
        delta = datetime.datetime.utcnow() - self.lifetime_start
        await self.send_uptime_message(ctx, "Total Lifetime Uptime", delta)

    async def send_uptime_message(self, ctx, title, delta):
        days, seconds = delta.days, delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        await ctx.send(f"{title}: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds.")

async def setup(bot):
    await bot.add_cog(Info(bot))
