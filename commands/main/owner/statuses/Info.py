from discord.ext import commands
from discord import Permissions
import discord
import datetime
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
        self.bot_start_time = datetime.datetime.utcnow()

    @discord.app_commands.command(name="ping", description="Shows the bot's latency and API ping.")
    async def ping(self, interaction: discord.Interaction):
        # Calculate the latency
        latency = round(self.bot.latency * 1000)  # in milliseconds

        # Measure the API ping
        before_api = discord.utils.utcnow()
        await interaction.response.defer()
        after_api = discord.utils.utcnow()
        api_ping = (after_api - before_api).total_seconds() * 1000

        embed = discord.Embed(title="Ping", color=discord.Color.dark_teal())
        embed.description = (
            f":satellite: **Latency**: {latency}ms\n"
            f":computer: **API Ping**: {api_ping}ms"
        )
        embed.set_footer(text="Pong!")

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="info", description="Provides detailed information about the bot.")
    async def info(self, interaction: discord.Interaction):
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
        
        embed = discord.Embed(title="Bot Stats", color=discord.Color.blue())

        embed.add_field(name=":satellite: Servers", value=str(total_guilds), inline=True)
        embed.add_field(name=":busts_in_silhouette: Users", value=str(total_users), inline=True)
        embed.add_field(name=":file_folder: Channels", value=str(total_channels), inline=True)
        embed.add_field(name=":speech_balloon: Text Channels", value=str(total_text_channels), inline=True)
        embed.add_field(name=":loud_sound: Voice Channels", value=str(total_voice_channels), inline=True)
        embed.add_field(name=":military_medal: Roles", value=str(total_roles), inline=True)
        embed.add_field(name=":stopwatch: API Latency", value=f"{api_latency} ms", inline=True)
        embed.add_field(name=":file_cabinet: Database Size", value=f"{database_size_readable} (Available: {available_space})", inline=True)

        await interaction.response.send_message(embed=embed)

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
        patch_hex = format(patch, 'x')
        return f"v{major}.{minor}.{patch_hex}"
        
async def setup(bot):
    await bot.add_cog(Info(bot))
