from discord.ext import commands
from TikTokLive import TikTokLiveClient
import asyncio

class TikTokLive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_trackers = {}

    @commands.command(usage="!tiktok <username>")
    async def tiktok(self, ctx, username: str):
        """Command to track a TikTok user's live status."""

        # Check if username is valid (basic check)
        if not username or username.startswith('@'):
            await ctx.send("Please provide a valid TikTok username.")
            return

        # Check if we're already tracking this user
        if username in self.live_trackers:
            await ctx.send(f"Already tracking TikTok user: {username}")
            return

        # Set up live tracking
        client = TikTokLiveClient(username)

        @client.on("connect")
        async def on_connect(_):
            await ctx.send(f"Connected to TikTok user {username}'s live stream.")

        @client.on("live")
        async def on_live(_):
            await ctx.send(f"{username} is now live on TikTok!")

        # Save the client for later shutdown
        self.live_trackers[username] = client

        # Start tracking in a non-blocking way
        asyncio.create_task(client.start())

    @commands.command(usage="!stoptracking <username>")
    async def stoptracking(self, ctx, username: str):
        """Stop tracking a TikTok user's live status."""
        if username in self.live_trackers:
            await self.live_trackers[username].stop()
            del self.live_trackers[username]
            await ctx.send(f"Stopped tracking TikTok user: {username}")
        else:
            await ctx.send(f"Not currently tracking TikTok user: {username}")

async def setup(bot):
    await bot.add_cog(TikTokLive(bot))
