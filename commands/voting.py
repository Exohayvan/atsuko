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
        self.running_votes = {}  # Store active voting tasks
        self.load_votes()

    def cog_unload(self):
        self.conn.close()

    async def resume_vote(self, title):
        vote_data = self.active_votes[title]
        channel = self.bot.get_channel(vote_data['channel_id'])
        start_time = datetime.datetime.strptime(vote_data['start_time'], "%Y-%m-%d %H:%M:%S.%f")
        end_time = start_time + datetime.timedelta(minutes=vote_data['duration'])

        while datetime.datetime.utcnow() < end_time:
            remaining_time = end_time - datetime.datetime.utcnow()
            minutes, seconds = divmod(remaining_time.seconds, 60)
            voting_message = await channel.fetch_message(vote_data['message_id'])
            embed = voting_message.embeds[0]
            embed.set_footer(text=f"Voting Ends in {remaining_time.days}d {minutes}m {seconds}s")
            await voting_message.edit(embed=embed)
            await asyncio.sleep(15)

        embed.set_footer(text="Voting Ended")
        await voting_message.edit(embed=embed)
        del self.active_votes[title]
        del self.running_votes[title]

    def load_votes(self):
        self.cursor.execute("SELECT * FROM active_votes")
        for row in self.cursor.fetchall():
            title, message_id, channel_id, option_emojis, votes, start_time, duration, voted_users = row
            self.active_votes[title] = {
                'message_id': message_id,
                'channel_id': channel_id,
                'option_emojis': json.loads(option_emojis),
                'votes': json.loads(votes),
                'start_time': start_time,
                'duration': duration,
                'voted_users': json.loads(voted_users),
            }
            self.running_votes[title] = self.bot.loop.create_task(self.resume_vote(title))

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

                    self.cursor.execute("""
                        UPDATE active_votes
                        SET option_emojis = ?, votes = ?, voted_users = ?
                        WHERE title = ?
                    """, (
                        json.dumps(vote_data['option_emojis']),
                        json.dumps(vote_data['votes']),
                        json.dumps(vote_data['voted_users']),
                        title,
                    ))
                    self.conn.commit()

                    await message.remove_reaction(reaction.emoji, user)
                break

    @commands.command()
    async def vote(self, ctx, time_limit, title, *options):
        if title in self.active_votes:
            await ctx.send("A vote with that title already exists.")
            return
        if len(options) < 2:
            await ctx.send("You need at least two options to start a vote.")
            return

        option_emojis = {f"{i+1}\N{combining enclosing keycap}": option for i, option in enumerate(options)}
        votes = {option: 0 for option in options}
        voted_users = {}

        embed = discord.Embed(title=title)
        for emoji, option in option_emojis.items():
            embed.add_field(name=option, value=f"{emoji}: 0", inline=False)

        message = await ctx.send(embed=embed)
        for emoji in option_emojis:
            await message.add_reaction(emoji)

        start_time = datetime.datetime.utcnow()

        self.active_votes[title] = {
            'message_id': message.id,
            'channel_id': message.channel.id,
            'option_emojis': option_emojis,
            'votes': votes,
            'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'duration': int(time_limit),
            'voted_users': voted_users,
        }
        self.running_votes[title] = self.bot.loop.create_task(self.run_vote(ctx, time_limit, title, *options))

        self.cursor.execute("""
            INSERT INTO active_votes VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            message.id,
            message.channel.id,
            json.dumps(option_emojis),
            json.dumps(votes),
            start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            int(time_limit),
            json.dumps(voted_users),
        ))
        self.conn.commit()

    async def run_vote(self, ctx, time_limit, title, *options):
        vote_data = self.active_votes[title]
        start_time = datetime.datetime.strptime(vote_data['start_time'], "%Y-%m-%d %H:%M:%S.%f")
        end_time = start_time + datetime.timedelta(minutes=vote_data['duration'])
        
        while datetime.datetime.utcnow() < end_time:
            remaining_time = end_time - datetime.datetime.utcnow()
            minutes, seconds = divmod(remaining_time.seconds, 60)
            voting_message = await ctx.fetch_message(vote_data['message_id'])
            embed = voting_message.embeds[0]
            embed.set_footer(text=f"Voting Ends in {remaining_time.days}d {minutes}m {seconds}s")
            await voting_message.edit(embed=embed)
            await asyncio.sleep(15)

        embed.set_footer(text="Voting Ended")
        await voting_message.edit(embed=embed)

        self.cursor.execute("DELETE FROM active_votes WHERE title = ?", (title,))
        self.conn.commit()

        del self.active_votes[title]
        del self.running_votes[title]

    @commands.command()
    async def endvote(self, ctx, title):
        if title not in self.active_votes:
            await ctx.send("There is no active vote with that title.")
            return

        vote_data = self.active_votes[title]
        message = await ctx.fetch_message(vote_data['message_id'])
        embed = message.embeds[0]
        embed.set_footer(text="Voting Ended")
        await message.edit(embed=embed)

        winner = max(vote_data['votes'], key=vote_data['votes'].get)
        await ctx.send(f"The winner of the vote '{title}' is: {winner}")

        self.cursor.execute("DELETE FROM active_votes WHERE title = ?", (title,))
        self.conn.commit()

        del self.active_votes[title]
        self.running_votes[title].cancel()
        del self.running_votes[title]

async def setup(bot):
    await bot.add_cog(Voting(bot))
