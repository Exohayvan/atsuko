import discord
from discord.ext import commands
import sqlite3
import asyncio
from sqlite3 import Error
from graphviz import Digraph

class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.create_connection()

        # Create necessary tables
        self.create_tables()

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect('./data/family.db') 
            print(sqlite3.version)
        except Error as e:
            print(e)
        return conn

    async def generate_family_tree(self, member_id):
        dot = Digraph(comment='Family Tree')
    
        # Create a cursor and select all accepted adoption requests involving the member
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT sender_id, receiver_id 
            FROM AdoptionRequests 
            WHERE accepted = 1 AND (sender_id = ? OR receiver_id = ?)
        """, (member_id, member_id))
    
        # Get all the rows
        relationships = cursor.fetchall()
    
        # Add edges for each relationship
        for relationship in relationships:
            # Get user objects using the IDs
            sender_user = await self.bot.fetch_user(relationship[0])
            receiver_user = await self.bot.fetch_user(relationship[1])
    
            # If the users exist, add them to the graph using their usernames
            if sender_user and receiver_user:
                dot.edge(sender_user.name, receiver_user.name)
    
        # Save the graph to a file with the username as the name
        user = await self.bot.fetch_user(member_id)
        filename = f'family_tree_{user.name}.gv'
        dot.render(filename, format='png', view=True)
        return filename  # Return the filename so it can be used later
                  
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create AdoptionRequests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AdoptionRequests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                receiver_id INTEGER,
                accepted INTEGER DEFAULT 0,
                FOREIGN KEY (sender_id) REFERENCES Users (id),
                FOREIGN KEY (receiver_id) REFERENCES Users (id)
            )
        """)
    
        # Create MarriageRequests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS MarriageRequests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                receiver_id INTEGER,
                accepted INTEGER DEFAULT 0,
                FOREIGN KEY (sender_id) REFERENCES Users (id),
                FOREIGN KEY (receiver_id) REFERENCES Users (id)
            )
        """)
    
        self.conn.commit()

    @commands.command(usage="!adopt <@member>")
    async def adopt(self, ctx, *, member: discord.Member):
        """Sends an adoption request to another member."""
        if ctx.author == member:
            await ctx.send(f"{ctx.author.mention}, you cannot send an adoption request to yourself.")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO AdoptionRequests(sender_id, receiver_id) VALUES (?, ?)", (ctx.author.id, member.id))
            self.conn.commit()
        except Error as e:
            print(e)

        # Send the adoption request message with reaction options
        message = await ctx.send(f"{member.mention}, do you want to be adopted by {ctx.author.mention}? React with ✅ to accept or 🚫 to reject.")

        # Add reaction options to the message
        await message.add_reaction("✅")  # Accept reaction
        await message.add_reaction("🚫")  # Reject reaction

        def check(reaction, user):
            return (
                user == member
                and reaction.message.id == message.id
                and str(reaction.emoji) in ["✅", "🚫"]
            )

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "✅":
                # Accept the adoption request
                cursor.execute(
                    "UPDATE AdoptionRequests SET accepted = 1 WHERE sender_id = ? AND receiver_id = ?",
                    (ctx.author.id, member.id),
                )
                self.conn.commit()
                await ctx.send(f"{member.mention} has accepted the adoption request from {ctx.author.mention}.")
            else:
                # Reject the adoption request
                cursor.execute(
                    "DELETE FROM AdoptionRequests WHERE sender_id = ? AND receiver_id = ?",
                    (ctx.author.id, member.id),
                )
                self.conn.commit()
                await ctx.send(f"{member.mention} has rejected the adoption request from {ctx.author.mention}.")
        except asyncio.TimeoutError:
            await ctx.send(f"The adoption request sent to {member.mention} timed out.")

    @commands.command(usage="!marry <@member>")
    async def marry(self, ctx, *, member: discord.Member):
        """Sends a marriage request to another member."""
        if ctx.author == member:
            await ctx.send(f"{ctx.author.mention}, you cannot send a marriage request to yourself.")
            return
    
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO MarriageRequests(sender_id, receiver_id) VALUES (?, ?)", (ctx.author.id, member.id))
            self.conn.commit()
        except Error as e:
            print(e)
    
        # Send the marriage request message with reaction options
        message = await ctx.send(f"{member.mention}, do you want to marry {ctx.author.mention}? React with ✅ to accept or 🚫 to reject.")
    
        # Add reaction options to the message
        await message.add_reaction("✅")  # Accept reaction
        await message.add_reaction("🚫")  # Reject reaction
    
        def check(reaction, user):
            return (
                user == member
                and reaction.message.id == message.id
                and str(reaction.emoji) in ["✅", "🚫"]
            )
    
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
    
            if str(reaction.emoji) == "✅":
                # Accept the marriage request
                cursor.execute(
                    "UPDATE MarriageRequests SET accepted = 1 WHERE sender_id = ? AND receiver_id = ?",
                    (ctx.author.id, member.id),
                )
                self.conn.commit()
                await ctx.send(f"{member.mention} has accepted the marriage request from {ctx.author.mention}.")
            else:
                # Reject the marriage request
                cursor.execute(
                    "DELETE FROM MarriageRequests WHERE sender_id = ? AND receiver_id = ?",
                    (ctx.author.id, member.id),
                )
                self.conn.commit()
                await ctx.send(f"{member.mention} has rejected the marriage request from {ctx.author.mention}.")
        except asyncio.TimeoutError:
            await ctx.send(f"The marriage request sent to {member.mention} timed out.")

    @commands.command(usage="!family")
    async def family(self, ctx):
        """Shows the family tree of the author."""
        filename = await self.generate_family_tree(ctx.author.id)
        await ctx.send(file=discord.File(f'{filename}.png'))
                
async def setup(bot):
    await bot.add_cog(Family(bot))
