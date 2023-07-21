from discord.ext import commands

class ChannelRelay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connected_channels = set()  # Store channel IDs

    # Add a channel to the connected channels list
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def connect_channel(self, ctx, channel: commands.TextChannelConverter):
        """Connects a channel for relaying."""
        self.connected_channels.add(channel.id)
        await ctx.send(f"Connected {channel.mention} for relaying messages.")

    # Remove a channel from the connected channels list
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disconnect_channel(self, ctx, channel: commands.TextChannelConverter):
        """Disconnects a channel from relaying."""
        self.connected_channels.discard(channel.id)
        await ctx.send(f"Disconnected {channel.mention} from relaying messages.")

    # Relay messages from one channel to all other connected channels
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id in self.connected_channels:
            for channel_id in self.connected_channels:
                if channel_id != message.channel.id:  # Don't send it to the originating channel
                    target_channel = self.bot.get_channel(channel_id)
                    if target_channel:  # Ensure the channel still exists
                        await target_channel.send(f"{message.author.display_name}: {message.content}")

async def setup(bot):
    await bot.add_cog(ChannelRelay(bot))
