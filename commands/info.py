from discord.ext import commands
from discord import Permissions
import datetime
import asyncio
import discord
import sqlite3

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime_start = datetime.datetime.utcnow()
        self.total_uptime = self.load_total_uptime()
        self.bot.loop.create_task(self.uptime_background_task())

    def load_total_uptime(self):
        try:
            with open("total_uptime.txt", "r") as f:
                total_uptime_seconds = int(f.read())
                return datetime.timedelta(seconds=total_uptime_seconds)
        except FileNotFoundError:
            return datetime.timedelta(seconds=0)

    def save_total_uptime(self):
        total_uptime_seconds = int(self.total_uptime.total_seconds())
        with open("total_uptime.txt", "w") as f:
            f.write(str(total_uptime_seconds))

    async def uptime_background_task(self):
        while True:
            current_uptime = datetime.datetime.utcnow() - self.uptime_start
            self.total_uptime += current_uptime
            self.save_total_uptime()
            self.uptime_start = datetime.datetime.utcnow()
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        self.uptime_start = datetime.datetime.utcnow()

    @commands.command()
    async def info(self, ctx):
        """Provides detailed information about the bot."""
        creation_time = self.bot.user.created_at
        owner_id = 276782057412362241  # change this to your user ID
        github_link = "https://github.com/Exohayvan/astuko"  # change this to your repository URL
        library_version = discord.__version__  # discord.py library version
        permissions = Permissions.all()
        invite_link = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions={permissions.value}&scope=bot"

        owner = await self.bot.fetch_user(owner_id)

        embed = discord.Embed(
            title="🤖 Bot Information",
            description=f"Here is some info about {self.bot.user.name}!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name=":bust_in_silhouette: Owner", value=f"{owner.name}#{owner.discriminator}", inline=True)
        embed.add_field(name=":calendar: Created On", value=creation_time.strftime("%B %d, %Y at %H:%M UTC"), inline=True)
        embed.add_field(name=":books: Library", value=f"discord.py {library_version}", inline=True)
        embed.add_field(name=":link: GitHub", value=f"[Repository]({github_link})", inline=True)
        embed.add_field(name=":mailbox_with_mail: Invite", value=f"[Click here]({invite_link})", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        """Generates an invite link for the bot."""
        permissions = Permissions.all()
        invite_link = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions={permissions.value}&scope=bot"
        await ctx.send(f"Invite me to your server using this link: {invite_link}")

    @commands.command()
    async def stats(self, ctx):
        """Shows the bot's current stats, including the number of guilds, users, and more."""
        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        total_text_channels = sum(len(guild.text_channels) for guild in self.bot.guilds)
        total_voice_channels = total_channels - total_text_channels
        total_roles = sum(len(guild.roles) for guild in self.bot.guilds)
        api_latency = round(self.bot.latency * 1000, 2)  # in milliseconds

        # Presence information
        total_online = total_idle = total_dnd = total_offline = 0
        for guild in self.bot.guilds:
            for member in guild.members:
                if str(member.status) == "online":
                    total_online += 1
                elif str(member.status) == "idle":
                    total_idle += 1
                elif str(member.status) == "dnd":
                    total_dnd += 1
                else:
                    total_offline += 1

        # Emoji count
        total_emojis = sum(len(guild.emojis) for guild in self.bot.guilds)

        embed = discord.Embed(title="Bot Stats", color=discord.Color.blue())

        embed.add_field(name=":satellite: Servers", value=str(total_guilds), inline=True)
        embed.add_field(name=":busts_in_silhouette: Users", value=str(total_users), inline=True)
        embed.add_field(name=":file_folder: Channels", value=str(total_channels), inline=True)
        embed.add_field(name=":speech_balloon: Text Channels", value=str(total_text_channels), inline=True)
        embed.add_field(name=":loud_sound: Voice Channels", value=str(total_voice_channels), inline=True)
        embed.add_field(name=":military_medal: Roles", value=str(total_roles), inline=True)
        embed.add_field(name=":stopwatch: API Latency", value=f"{api_latency} ms", inline=True)
        embed.add_field(name=":green_heart: Online Users", value=str(total_online), inline=True)
        embed.add_field(name=":yellow_heart: Idle Users", value=str(total_idle), inline=True)
        embed.add_field(name=":heart: DND Users", value=str(total_dnd), inline=True)
        embed.add_field(name=":black_heart: Offline Users", value=str(total_offline), inline=True)
        embed.add_field(name=":smiley: Emojis", value=str(total_emojis), inline=True)

        # Most used commands
        number_of_commands = 3
        conn = sqlite3.connect('./data/command_usage.db')
        c = conn.cursor()

        # Get the most used commands
        c.execute('SELECT command_name, SUM(usage_count) as total_usage FROM CommandUsage GROUP BY command_name ORDER BY total_usage DESC LIMIT ?', (number_of_commands,))

        most_used_commands = c.fetchall()
        conn.close()

        # Add most used commands to the embed
        if most_used_commands:
            embed.add_field(name="Most Used Commands", value="\n".join(f"**{command[0]}**: {command[1]} uses" for command in most_used_commands), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """Shows the current uptime of the bot since last reboot."""
        current_uptime = datetime.datetime.utcnow() - self.uptime_start
        await self.send_uptime_message(ctx, "Current Uptime", current_uptime)

    @commands.command()
    async def lifetime(self, ctx):
        """Shows the total lifetime uptime of the bot."""
        # Lifetime uptime includes current uptime
        current_uptime = datetime.datetime.utcnow() - self.uptime_start
        total_uptime = self.total_uptime + current_uptime
        await self.send_uptime_message(ctx, "Total Lifetime Uptime", total_uptime)

    async def send_uptime_message(self, ctx, title, delta):
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60
        seconds = delta.seconds % 60

        uptime_string = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds."

        embed = discord.Embed(title=title, color=discord.Color.blue())
        embed.add_field(name="Uptime", value=uptime_string, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
