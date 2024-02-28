from discord.ext import commands
from discord import Permissions
import discord
import datetime
import asyncio
import discord
import sqlite3
import os
import shutil
import math
import subprocess

def get_directory_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    return total

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_available_space(path='.'):
    total, used, free = shutil.disk_usage(path)
    return convert_size(free)

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime_start = datetime.datetime.utcnow()
        self.init_db()
        self.init_daily_uptime_db()
        self.migrate_from_file_if_exists()
        self.bot_start_time = datetime.datetime.utcnow()
        self.total_uptime = self.load_total_uptime()
        self.bot.loop.create_task(self.uptime_background_task())

    def connect_db(self):
        """Connects to the specific database."""
        rv = sqlite3.connect('./data/uptime.db')
        rv.row_factory = sqlite3.Row
        return rv
        
    def init_daily_uptime_db(self):
        """Initializes the daily uptime database."""
        db = self.connect_db()
        db.execute("CREATE TABLE IF NOT EXISTS daily_uptime (date DATE, uptime INTEGER);")
        db.commit()
    
    def init_db(self):
        """Initializes the database."""
        db = self.connect_db()
        db.execute("CREATE TABLE IF NOT EXISTS uptime (total_uptime INTEGER);")
        db.execute("INSERT INTO uptime (total_uptime) SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM uptime);")
        db.commit()

    def migrate_from_file_if_exists(self):
        """If total_uptime.txt exists, migrate its data to the database and delete the file."""
        if os.path.exists("total_uptime.txt"):
            with open("total_uptime.txt", "r") as f:
                total_uptime_seconds = int(f.read())
                self.save_total_uptime(total_uptime_seconds)
                os.remove("total_uptime.txt")

    def format_timedelta(self, delta):
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds."

    def load_total_uptime(self):
        db = self.connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT total_uptime FROM uptime")
        total_uptime_seconds = cursor.fetchone()[0]
        return datetime.timedelta(seconds=total_uptime_seconds)

    def save_total_uptime(self, total_uptime_seconds=None):
        if total_uptime_seconds is None:
            total_uptime_seconds = int(self.total_uptime.total_seconds())
        db = self.connect_db()
        db.execute("UPDATE uptime SET total_uptime = ?", (total_uptime_seconds,))
        db.commit()

    async def uptime_background_task(self):
        while True:
            await asyncio.sleep(10)
            current_uptime = datetime.datetime.utcnow() - self.uptime_start
            self.total_uptime += current_uptime
            self.save_total_uptime()
            self.save_daily_uptime(current_uptime)  # save the current uptime to the daily uptime database
            self.uptime_start += datetime.timedelta(seconds=10)  # increment the start time by 10 seconds
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.uptime_start = datetime.datetime.utcnow()
        
    @discord.app_commands.command(name="ping", description="Shows the bot's latency and API ping.")
    async def ping(self, interaction: discord.Interaction):
        # Calculate the latency
        latency = round(self.bot.latency * 1000)  # in milliseconds

        # Measure the API ping
        before_api = discord.utils.utcnow()
        await interaction.response.defer()
        after_api = discord.utils.utcnow()
        api_ping = (after_api - before_api).total_seconds() * 1000

        # Measure the database ping (example placeholder)
        before_db = discord.utils.utcnow()
        # Perform a database operation here, replace with actual database query
        after_db = discord.utils.utcnow()
        db_ping = (after_db - before_db).total_seconds() * 1000

        embed = discord.Embed(title="Ping", color=discord.Color.dark_teal())
        embed.description = (
            f":satellite: **Latency**: {latency}ms\n"
            f":computer: **API Ping**: {api_ping}ms\n"
            f":floppy_disk: **Database Ping**: {db_ping}ms"
        )
        embed.set_footer(text="Pong!")

        await interaction.followup.send(embed=embed)
                        
    @discord.app_commands.command(name="info", description="Provides detailed information about the bot.")
    async def info(self, interaction: discord.Interaction):
        """Provides detailed information about the bot."""
        creation_time = self.bot.user.created_at
        owner_id = 276782057412362241  # Change this to your user ID
        github_link = "https://github.com/Exohayvan/astuko"  # Change this to your repository URL
        library_version = discord.__version__  # discord.py library version
        permissions = discord.Permissions.all()
        invite_link = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions={permissions.value}&scope=bot%20applications.commands"

        owner = await self.bot.fetch_user(owner_id)

        embed = discord.Embed(
            title="🤖 Bot Information",
            description=f"Here is some info about {self.bot.user.name}!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name="👤 Owner", value=f"{owner.name}#{owner.discriminator}", inline=True)
        embed.add_field(name="📅 Created On", value=creation_time.strftime("%B %d, %Y at %H:%M UTC"), inline=True)
        embed.add_field(name="📚 Library", value=f"discord.py {library_version}", inline=True)
        embed.add_field(name="🔗 GitHub", value=f"[Repository]({github_link})", inline=True)
        embed.add_field(name="📩 Invite", value=f"[Click here]({invite_link})", inline=True)

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="invite", description="Generates an invite link for the bot.")
    async def invite(self, interaction: discord.Interaction):
        """Generates an invite link for the bot."""
        permissions = discord.Permissions.all()
        invite_link = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions={permissions.value}&scope=bot%20applications.commands"
        embed = discord.Embed(title="Invite Me", description=f"[Click Here]({invite_link}) to invite me to your server!", color=0x7289da)
        await interaction.response.send_message(embed=embed)
        
    @discord.app_commands.command(name="stats", description="Shows the bot's current stats.")
    async def stats(self, interaction: discord.Interaction):
        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        total_text_channels = sum(len(guild.text_channels) for guild in self.bot.guilds)
        total_voice_channels = total_channels - total_text_channels
        total_roles = sum(len(guild.roles) for guild in self.bot.guilds)
        api_latency = round(self.bot.latency * 1000, 2)
        database_size = get_directory_size('./data')
        database_size_readable = convert_size(database_size)
        available_space = get_available_space('./data')
        
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

        total_emojis = sum(len(guild.emojis) for guild in self.bot.guilds)

        embed = discord.Embed(title="Bot Stats", color=discord.Color.blue())
        # Add fields to your embed as in your original command

        conn = sqlite3.connect('./data/command_usage.db')
        c = conn.cursor()
        c.execute('SELECT command_name, SUM(usage_count) as total_usage FROM CommandUsage GROUP BY command_name ORDER BY total_usage DESC LIMIT ?', (3,))
        most_used_commands = c.fetchall()
        conn.close()

        if most_used_commands:
            embed.add_field(name="Most Used Commands", value="\n".join(f"**{command[0]}**: {command[1]} uses" for command in most_used_commands), inline=False)

        await interaction.response.send_message(embed=embed)

    async def uptime_background_task(self):
        while True:
            await asyncio.sleep(60)
            current_uptime = datetime.datetime.utcnow() - self.uptime_start
            self.total_uptime += current_uptime
            self.save_total_uptime()
            self.save_daily_uptime(current_uptime)  # save the current uptime to the daily uptime database
            self.uptime_start += datetime.timedelta(minutes=1)
            
    def get_uptime_for_last_30_days(self):
        date_today = datetime.date.today()
        cutoff_date = date_today - datetime.timedelta(days=30)
    
        db = self.connect_db()
        cursor = db.cursor()
    
        # Get the sum of the uptime for the last 30 days
        cursor.execute("SELECT SUM(uptime) as total_uptime FROM daily_uptime WHERE date >= ?", (cutoff_date,))
        result = cursor.fetchone()
    
        return datetime.timedelta(seconds=result['total_uptime'] if result['total_uptime'] else 0)
    
    def save_daily_uptime(self, current_uptime):
        date_today = datetime.date.today()
        daily_uptime_seconds = int(current_uptime.total_seconds())
    
        db = self.connect_db()
        cursor = db.cursor()
    
        # Check if today's record already exists
        cursor.execute("SELECT * FROM daily_uptime WHERE date = ?", (date_today,))
        record = cursor.fetchone()
    
        if record:
            # If today's record exists, update it
            new_daily_uptime_seconds = record['uptime'] + daily_uptime_seconds
            cursor.execute("UPDATE daily_uptime SET uptime = ? WHERE date = ?", (new_daily_uptime_seconds, date_today))
        else:
            # If today's record does not exist, insert it
            cursor.execute("INSERT INTO daily_uptime (date, uptime) VALUES (?, ?)", (date_today, daily_uptime_seconds))
    
        # Delete records older than 31 days
        cutoff_date = date_today - datetime.timedelta(days=31)
        cursor.execute("DELETE FROM daily_uptime WHERE date < ?", (cutoff_date,))
    
        db.commit()
    
    def get_uptime_for_last_7_days(self):
        date_today = datetime.date.today()
        cutoff_date = date_today - datetime.timedelta(days=7)
        
        db = self.connect_db()
        cursor = db.cursor()
        
        # Get the sum of the uptime for the last 7 days
        cursor.execute("SELECT SUM(uptime) as total_uptime FROM daily_uptime WHERE date >= ?", (cutoff_date,))
        result = cursor.fetchone()
        
        return datetime.timedelta(seconds=result['total_uptime'] if result['total_uptime'] else 0)
    
    @commands.command(usage="!uptime")
    async def uptime(self, ctx):
        """Shows the current uptime of the bot since last restart."""
        current_uptime = datetime.datetime.utcnow() - self.bot_start_time
        total_uptime = self.total_uptime + current_uptime
        uptime_last_30_days = self.get_uptime_for_last_30_days()
        total_seconds_last_30_days = 30 * 24 * 60 * 60
        uptime_percentage_last_30_days = (uptime_last_30_days.total_seconds() / total_seconds_last_30_days) * 100
    
        # Uptime for last 7 days
        uptime_last_7_days = self.get_uptime_for_last_7_days()
        total_seconds_last_7_days = 7 * 24 * 60 * 60
        uptime_percentage_last_7_days = (uptime_last_7_days.total_seconds() / total_seconds_last_7_days) * 100
    
        embed = discord.Embed(title="Current Uptime", color=discord.Color.blue())
        embed.add_field(name="Since Last Restart", value=self.format_timedelta(current_uptime), inline=False)
        embed.add_field(name="Lifetime", value=self.format_timedelta(total_uptime), inline=False)
        embed.add_field(name="Last 30 Days", value=f"{uptime_percentage_last_30_days:.2f}% of total time", inline=False)
        embed.add_field(name="Last 7 Days", value=f"{uptime_percentage_last_7_days:.2f}% of total time", inline=False)
    
        await ctx.send(embed=embed)
        
    @commands.command(usage="!lifetime")
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

    @commands.command(usage="!version")
    async def version(self, ctx):
        """Shows the current version of the bot based on Git commits and the hash of the last commit."""
        commit_count, last_commit_hash = self.get_git_commit_count_and_hash()
        version = self.format_version(commit_count)
        await ctx.send(f"Current Version: {version} (Last Commit Hash: {last_commit_hash})")
    
    def get_git_commit_count_and_hash(self):
        """Returns the number of commits and the hash of the last commit in the Git repository."""
        try:
            count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], stderr=subprocess.STDOUT).strip()
            last_commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT).strip()
            return int(count), last_commit_hash.decode('utf-8')
        except subprocess.CalledProcessError as e:
            print(f"Git command error: {e.output.decode()}")
            return 0, "unknown"
        except Exception as e:
            print(f"Error getting commit count and hash: {e}")
            return 0, "unknown"

    def format_version(self, count):
        """Formats the commit count into a version string."""
        major = count // 1000
        minor = (count // 100) % 10
        patch = count % 100
        # Convert patch to hexadecimal
        patch_hex = format(patch, 'x')
        return f"v{major}.{minor}.{patch_hex}"
        
async def setup(bot):
    await bot.add_cog(Info(bot))
