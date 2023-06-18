from discord.ext import commands
import discord
import asyncio
import datetime

class Voting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_votes = {}

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        message = reaction.message
        for title, vote_data in self.active_votes.items():
            if message.id == vote_data['message_id']:
                emoji = str(reaction.emoji)
                if emoji in vote_data['option_emojis']:
                    option = vote_data['option_emojis'][emoji]

                    # If the user has already voted for a different option, remove their old vote
                    if user.id in vote_data['voted_users']:
                        old_option = vote_data['voted_users'][user.id]
                        if old_option != option:
                            vote_data['votes'][old_option] -= 1

                    vote_data['votes'][option] += 1
                    vote_data['voted_users'][user.id] = option
                    await message.remove_reaction(reaction.emoji, user)
                break

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

        # Add the message_id, option_emojis, votes, and voted_users to the active_votes data
        self.active_votes[title] = {
            'message_id': voting_message.id,
            'option_emojis': option_emojis,
            'votes': {option: 0 for option in options},
            'end_time': end_time,
            'voted_users': {}
        }

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
        max_votes = max(self.active_votes[title]['votes'].values())
        winning_options = [option for option, votes in self.active_votes[title]['votes'].items() if votes == max_votes]

        # Create an embedded message with the winning option(s)
        winning_embed = discord.Embed(title="Voting Results", description="The vote has ended. Here are the winning option(s):")
        for i, option in enumerate(winning_options):
            winning_embed.add_field(name=f"Option {i+1}", value=option, inline=False)

        await ctx.send(embed=winning_embed)
        del self.active_votes[title]  # Clean up after the vote is finished

async def setup(bot):
    await bot.add_cog(Voting(bot))
