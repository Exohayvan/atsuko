from discord.ext import commands
import discord
import logging

# Setup logging
logger = logging.getLogger('Leaderboard.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/Leaderboard.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False

class InviteLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}  # Format: {guild_id: {invite_code: invite_count}}
        bot.loop.create_task(self.cache_invites())

    async def cache_invites(self):
        """Cache invites for all guilds."""
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            self.invites[guild.id] = {}
            try:
                for invite in await guild.invites():
                    self.invites[guild.id][invite.code] = invite.uses
            except discord.HTTPException as e:
                logger.error(f"Failed to cache invites for guild {guild.id}: {e}")
        logger.info("Invites cached.")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """Update cache on invite creation."""
        self.invites[invite.guild.id][invite.code] = invite.uses

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """Update cache on invite deletion."""
        if invite.guild.id in self.invites:
            self.invites[invite.guild.id].pop(invite.code, None)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Update leaderboard on member join."""
        new_invites = {i.code: i.uses for i in await member.guild.invites()}
        for code, uses in new_invites.items():
            if uses > self.invites[member.guild.id].get(code, 0):
                logger.info(f"Member {member} joined using invite {code}")
                self.invites[member.guild.id][code] = uses
                break

    @commands.command()
    async def leaderboard(self, ctx):
        """Display the invite leaderboard."""
        guild_id = ctx.guild.id
        if guild_id in self.invites:
            leaderboard_data = sorted(self.invites[guild_id].items(), key=lambda x: x[1], reverse=True)
            leaderboard_message = "Invite Leaderboard:\n"
            for code, uses in leaderboard_data:
                leaderboard_message += f"Code: {code} - Uses: {uses}\n"
            await ctx.send(leaderboard_message)
        else:
            await ctx.send("Leaderboard data is not available.")

async def setup(bot):
    await bot.add_cog(InviteLeaderboard(bot))
