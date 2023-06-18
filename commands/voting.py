import discord
from discord.ext import commands
import asyncio
import datetime
import sqlite3
import json

class Voting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('./data/voting.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_votes (
                title TEXT PRIMARY KEY,
                message_id INTEGER,
                option_emojis TEXT,
                votes TEXT,
                end_time TEXT,
                voted_users TEXT
            )
        """)
        self.conn.commit()
        self.active_votes = {}
        self.load_votes()

    def cog_unload(self):
        self.conn.close()

    def load_votes(self):
        self.cursor.execute("SELECT * FROM active_votes")
        for row in self.cursor.fetchall():
            title, message_id, option_emojis, votes, end_time, voted_users = row
            self.active_votes[title] = {
                'message_id': message_id,
                'option_emojis': json.loads(option_emojis),
                'votes': json.loads(votes),
                'end_time': datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f"),
                'voted_users': json.loads(voted_users),
            }

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

                    if user.id in vote_data['voted_users']:
                        old_option = vote_data['voted_users'][user.id]
                        if old_option != option:
                            vote_data['votes'][old_option] -= 1

                    vote_data['votes'][option] += 1
                    vote_data['voted_users'][user.id] = option

                    await user.send(f"Your vote for '{title}' has been changed to: {option}")

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

        embed = discord.Embed(title=f"Vote: {title}", description="React with the number emojis to vote. Votes are anonymous and reaction will disappear after voting. Only last selection will be tracked. Votes after vote ends, will not count.")
        option_emojis = {f"{i+1}\u20e3": option for i, option in enumerate(options)}
        for i, option in enumerate(options):
            emoji = f"{i+1}\u20e3"  
            embed.add_field(name=f"Option {i+1}", value=f"{option} {emoji}", inline=False)
        voting_message = await ctx.send(embed=embed)

        for i in range(len(options)):
            emoji = f"{i+1}\u20e3"  
            await voting_message.add_reaction(emoji)

        self.active_votes[title] = {
            'message_id': voting_message.id,
            'option_emojis': option_emojis,
            'votes': {option: 0 for option in options},
            'end_time': end_time,
            'voted_users': {}
        }
        
        self.cursor.execute("INSERT INTO active_votes VALUES (?, ?, ?, ?, ?, ?)",
                            (title, voting_message.id, json.dumps(option_emojis), json.dumps({option: 0 for option in options}),
                            str(end_time), json.dumps({})))
        self.conn.commit()

        while datetime.datetime.utcnow() < end_time:
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

        max_votes = max(self.active_votes[title]['votes'].values())
        winning_options = [option for option, votes in self.active_votes[title]['votes'].items() if votes == max_votes]

        winning_embed = discord.Embed(title="Voting Results", description="The vote has ended. Here are the winning option(s):")
        for i, option in enumerate(winning_options):
            winning_embed.add_field(name=f"Option {i+1}", value=option, inline=False)

        await ctx.send(embed=winning_embed)
        del self.active_votes[title]

async def setup(bot):
    await bot.add_cog(Voting(bot))
