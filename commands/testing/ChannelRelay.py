import discord
from discord.ext import commands, tasks
import datetime

class ChannelRelay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connected_channels = set()
        self.last_message_times = {}  # Stores the last time a message was sent in a channel: {channel_id: datetime.datetime}
        self.safety_message = (
            "🔒 **Online Safety Reminder** 🔒\n\n"
            "- Always be cautious when sharing personal information. Avoid sharing your real name, address, phone number, or other identifiable details.\n"
            "- Remember that people online might not be who they say they are. Strangers can misrepresent themselves.\n"
            "- Never agree to meet someone you've only spoken to online without consulting a trusted adult. If you must meet, do so in a public place and bring a friend or family member.\n"
            "- Be wary of suspicious links or downloads. They could contain malware or phishing schemes.\n"
            "- If something or someone makes you uncomfortable, trust your instincts, and seek guidance from a trusted individual or report the behavior.\n"
            "- Remember to use strong and unique passwords for your online accounts. Avoid using easily guessable passwords like 'password123'.\n"
            "- It's okay to take breaks from online interactions. Your mental health and well-being are important.\n\n"
            "Stay safe and always prioritize your safety first!"
        )
        self.check_for_reminder.start()  # Start the periodic task

    @tasks.loop(minutes=1)  # Check every minute
    async def check_for_reminder(self):
        for guild_id, channel_id in self.connected_channels:
            if channel_id in self.last_message_times:
                elapsed_time = datetime.datetime.now() - self.last_message_times[channel_id]
                if elapsed_time > datetime.timedelta(minutes=15):
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(self.safety_message)
                        del self.last_message_times[channel_id]  # Remove the channel_id to avoid repeated reminders until a new message is sent

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if (message.guild.id, message.channel.id) in self.connected_channels:
            self.last_message_times[message.channel.id] = datetime.datetime.now()
            for guild_id, channel_id in self.connected_channels:
                if guild_id != message.guild.id or channel_id != message.channel.id:
                    target_guild = self.bot.get_guild(guild_id)
                    if target_guild:
                        target_channel = target_guild.get_channel(channel_id)
                        if target_channel:
                            await target_channel.send(f"{message.author.display_name}: {message.content}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def connect_channel(self, ctx, channel: discord.TextChannel=None):
        """Connects a channel for relaying."""
        if not channel:
            channel = ctx.channel
        self.connected_channels.add((ctx.guild.id, channel.id))
        await ctx.send(f"Connected {channel.mention} for relaying messages.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disconnect_channel(self, ctx, channel: discord.TextChannel=None):
        """Disconnects a channel from relaying."""
        if not channel:
            channel = ctx.channel
        self.connected_channels.discard((ctx.guild.id, channel.id))
        await ctx.send(f"Disconnected {channel.mention} from relaying messages.")

async def setup(bot):
    await bot.add_cog(ChannelRelay(bot))