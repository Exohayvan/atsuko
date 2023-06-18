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
        if title in self.active_votes:
            await ctx.send("There is already an active vote with that title.")
            return

        if len(options) < 2 or len(options) > 10:
            await ctx.send("Please provide between 2 and 10 voting options.")
            return

        time_limit = time_limit.lower()
        time_formats = {
            "d": ("days", 24),
            "h": ("hours", 60),
            "m": ("minutes", 1)
        }

        unit = time_limit[-1]
        if unit not in time_formats:
            await ctx.send("Please provide a valid time limit format. Use 'd' for days, 'h' for hours, or 'm' for minutes.")
            return

        try:
            amount = int(time_limit[:-1])
        except ValueError:
            await ctx.send("Please provide a valid time limit.")
            return

        if amount < 1:
            await ctx.send("Time limit must be at least 1 unit.")
            return

        time_name, multiplier = time_formats[unit]
        end_time = datetime.datetime.utcnow() + datetime.timedelta(**{time_name: amount * multiplier})

        self.active_votes[title] = {option: 0 for option in options}

        # Remove the user's message
        await ctx.message.delete()

        # Create and send an embedded message with voting details
        embed = discord.Embed(title=f"Vote: {title}", description="React with the number emojis to vote.")
        option_emojis = {f"{i+1}\u20e3": option for i, option in enumerate(options)}
        for i, option in enumerate(options):
            emoji = f"{i+1}\u20e3"  # Generate number emojis
            embed.add_field(name=f"Option {i+1}", value=f"{option} {emoji}", inline=False)
        voting_message = await ctx.send(embed=embed)

        # React with corresponding emojis
        for i in range(len(options)):
            emoji = f"{i+1}\u20e3"  # Generate number emojis
            await voting_message.add_reaction(emoji)

        while datetime.datetime.utcnow() < end_time:
            # Update the vote counts based on reactions
            updated_voting_message = await ctx.fetch_message(voting_message.id)
            for reaction in updated_voting_message.reactions:
                if str(reaction.emoji) in option_emojis:
                    self.active_votes[title][option_emojis[str(reaction.emoji)]] = reaction.count - 1

            remaining_time = end_time - datetime.datetime.utcnow()
            minutes, seconds = divmod(remaining_time.seconds, 60)
            embed.set_footer(text=f"Voting Ends in {remaining_time.days}d {minutes}m {seconds}s")
            await voting_message.edit(embed=embed)
            await asyncio.sleep(15)

        updated_voting_message = await ctx.fetch_message(voting_message.id)
        embed.set_footer(text="Voting Ended")

        # Determine the winning option(s)
        max_votes = max(self.active_votes[title].values())
        winning_options = [option for option, votes in self.active_votes[title].items() if votes == max_votes]

        # Add ✅ emoji beside winning option(s)
        for field in embed.fields:
            if option_emojis[field.value[-2:]] in winning_options: # Check the emoji associated with each field
                field.name += " ✅"

        await updated_voting_message.edit(embed=embed)
        del self.active_votes[title]  # Clean up after the vote is finished

async def setup(bot):
    await bot.add_cog(Voting(bot))
