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
                channel_id INTEGER,
                option_emojis TEXT,
                votes TEXT,
                start_time TEXT,
                duration INTEGER,
                voted_users TEXT
            )
        """)
        self.conn.commit()
        self.active_votes = {}
        self.load_votes()
        self.bot.loop.create_task(self.check_end_times())

    def cog_unload(self):
        self.conn.close()

    def load_votes(self):
        self.cursor.execute("SELECT * FROM active_votes")
        for row in self.cursor.fetchall():
            title, message_id, channel_id, option_emojis, votes, start_time, duration, voted_users = row
            self.active_votes[title] = {
                'message_id': message_id,
                'channel_id': channel_id,
                'option_emojis': json.loads(option_emojis),
                'votes': json.loads(votes),
                'start_time': datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f"),
                'duration': duration,
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
            "d": ("days", 24 * 60),
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

        duration = amount * time_formats[unit][1]
        start_time = datetime.datetime.utcnow()

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
            'channel_id': ctx.channel.id,
            'option_emojis': option_emojis,
            'votes': {option: 0 for option in options},
            'start_time': start_time,
            'duration': duration,
            'voted_users': {}
        }

        self.cursor.execute("INSERT INTO active_votes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (title, voting_message.id, ctx.channel.id, json.dumps(option_emojis), json.dumps({option: 0 for option in options}),
                            str(start_time), duration, json.dumps({})))
        self.conn.commit()

    async def check_end_times(self):
        while True:
            for title, vote_data in list(self.active_votes.items()):
                start_time = vote_data['start_time']
                duration = vote_data['duration']
                end_time = start_time + datetime.timedelta(minutes=duration)
                if datetime.datetime.utcnow() >= end_time:
                    channel = self.bot.get_channel(vote_data['channel_id'])
                    if channel:
                        max_votes = max(vote_data['votes'].values())
                        winning_options = [option for option, votes in vote_data['votes'].items() if votes == max_votes]

                        winning_embed = discord.Embed(title="Voting Results", description="The vote has ended. Here are the winning option(s):")
                        for i, option in enumerate(winning_options):
                            winning_embed.add_field(name=f"Option {i+1}", value=option, inline=False)

                        await channel.send(embed=winning_embed)

                    self.cursor.execute("DELETE FROM active_votes WHERE title = ?", (title,))
                    self.conn.commit()
                    del self.active_votes[title]

            await asyncio.sleep(15)

async def setup(bot):
    await bot.add_cog(Voting(bot))
