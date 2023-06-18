from discord.ext import commands
import discord
import asyncio
import datetime

class Voting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_votes = {}
        
    @commands.command()
    async def vote(self, ctx, time_limit, title, *options):
        """Starts a voting process."""
        if title in self.active_votes:
            await ctx.send("There is already an active vote with that title.")
            return

        if len(options) < 2 or len(options) > 10:
            await ctx.send("Please provide between 2 and 10 voting options.")
            return

        try:
            time_limit = int(time_limit)
        except ValueError:
            await ctx.send("Please provide a valid time limit in hours.")
            return

        if time_limit < 1:
            await ctx.send("Time limit must be at least 1 hour.")
            return

        self.active_votes[title] = {option: 0 for option in options}

        # Remove the user's message
        await ctx.message.delete()

        # Create and send an embedded message with voting details
        embed = discord.Embed(title=f"Vote: {title}", description="React with the number emojis to vote.")
        for i, option in enumerate(options):
            emoji = f"{i+1}\u20e3"  # Generate number emojis
            embed.add_field(name=f"Option {i+1}", value=f"{option} {emoji}", inline=False)
        voting_message = await ctx.send(embed=embed)

        # React with corresponding emojis
        for i in range(len(options)):
            emoji = f"{i+1}\u20e3"  # Generate number emojis
            await voting_message.add_reaction(emoji)

        end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=time_limit)

        while datetime.datetime.utcnow() < end_time:
            remaining_time = end_time - datetime.datetime.utcnow()
            minutes, seconds = divmod(remaining_time.seconds, 60)
            embed.set_footer(text=f"Voting Ends in {remaining_time.days}d {minutes}m {seconds}s")
            await voting_message.edit(embed=embed)
            await asyncio.sleep(60)

        updated_voting_message = await ctx.fetch_message(voting_message.id)
        embed.set_footer(text="Voting Ended")
        await updated_voting_message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Voting(bot))
