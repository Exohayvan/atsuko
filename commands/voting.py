import discord
from discord.ext import commands
import asyncio
import datetime
import sqlite3
import json
from discord.errors import NotFound

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

        winner = max(vote_data['votes'], key=vote_data['votes'].get)

        # create a new embed object for the winner announcement
        winner_embed = discord.Embed(title=f"Vote Results for '{title}'", description=f"The winner is: {winner}", color=0x00ff00)
        await channel.send(embed=winner_embed)

    def load_votes(self):
        self.cursor.execute("SELECT * FROM active_votes")
        for row in self.cursor.fetchall():
            title, message_id, channel_id, option_emojis, votes, start_time, duration, voted_users = row
            self.active_votes[title] = {
                'message_id': message_id,
                'channel_id': channel_id,
                'option_emojis': json.loads(option_emojis),
                'votes': {emoji: 0 for emoji in json.loads(option_emojis).keys()},  # Reset votes count to 0
                'start_time': start_time,
                'duration': duration,
                'voted_users': json.loads(voted_users),
            }
            self.running_votes[title] = self.bot.loop.create_task(self.recount_votes(title))  # Recount existing votes
            self.running_votes[title] = self.bot.loop.create_task(self.resume_vote(title))  # Resume countdown

    async def recount_votes(self, title):
        vote_data = self.active_votes[title]
        channel = self.bot.get_channel(vote_data['channel_id'])
        message = await channel.fetch_message(vote_data['message_id'])

        # Create a set to keep track of voted users
        voted_users = set(vote_data['voted_users'])
        print(f"Current voted users: {voted_users}")  # Debug print

        # Process reactions only on the voting message
        if message.author == self.bot.user:
            for reaction in message.reactions:
                async for user in reaction.users():
                    if user == self.bot.user:
                        continue
                    emoji = str(reaction.emoji)
                    if emoji in vote_data['option_emojis']:
                        print(f"Processing vote for emoji: {emoji}, user: {user.name}")  # Debug print
                        if user.id not in voted_users:
                            vote_data['votes'][emoji] += 1
                            voted_users.add(user.id)
                            try:
                                await message.remove_reaction(reaction.emoji, user)  # Remove user reaction
                            except NotFound:
                                pass  # Handle case when reaction is not found

        # Update the 'voted_users' list after processing all reactions
        vote_data['voted_users'] = list(voted_users)
        print(f"Updated voted users: {vote_data['voted_users']}")  # Debug print

    @commands.Cog.listener()
    async def on_ready(self):
        # When the bot starts/restarts, recount votes for all active votes
        for title in self.active_votes:
            self.bot.loop.create_task(self.recount_votes(title))
            self.bot.loop.create_task(self.resume_vote(title))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        print(f"Reaction added: {reaction.emoji} by user {user.name}")

        message = reaction.message
        for title, vote_data in self.active_votes.items():
            if message.id == vote_data['message_id']:
                emoji = str(reaction.emoji)
                if emoji in vote_data['option_emojis'].keys():
                    if user.id not in vote_data['voted_users']:
                        print(f"Valid vote by {user.name} on option {emoji}")
                        vote_data['votes'][emoji] += 1
                        vote_data['voted_users'].append(user.id)
                        await self.update_vote_count(title)  # Update the vote count in the message
                        try:
                            await reaction.remove(user)  # Remove user reaction
                        except NotFound:
                            pass  # Handle case when reaction is not found
                    else:
                        print(f"User {user.name} has already voted!")
                    break

    async def update_vote_count(self, title):
        vote_data = self.active_votes[title]
        channel = self.bot.get_channel(vote_data['channel_id'])
        voting_message = await channel.fetch_message(vote_data['message_id'])
        embed = discord.Embed(title=title)
        for emoji, option in vote_data['option_emojis'].items():
            vote_count = vote_data['votes'][emoji]
            embed.add_field(name=option, value=f"{emoji}: {vote_count}", inline=False)
        print(f"Updating vote count: {vote_data['votes']}")
        await voting_message.edit(embed=embed)

    @commands.command()
    async def vote(self, ctx, time_limit, title, *options):
        if title in self.active_votes:
            await ctx.send("A vote with that title already exists.")
            return
        if len(options) < 2:
            await ctx.send("You need at least two options to start a vote.")
            return

        option_emojis = {f"{i+1}\N{combining enclosing keycap}": option for i, option in enumerate(options)}
        votes = {emoji: 0 for emoji in option_emojis.keys()}
        voted_users = []

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
        self.cursor.execute("""
            INSERT INTO active_votes (title, message_id, channel_id, option_emojis, votes, start_time, duration, voted_users)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

        self.running_votes[title] = self.bot.loop.create_task(self.resume_vote(title))

async def setup(bot):
    await bot.add_cog(Voting(bot))
