import discord
from discord.ext import commands
import sqlite3
import asyncio
from sqlite3 import Error

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

    def create_tables(self):
        cursor = self.conn.cursor()
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
        
        self.conn.commit()

    @commands.command()
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

    @commands.command()
    async def accept_marriage(self, ctx):
        """Accepts a marriage proposal."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM MarriageRequests WHERE receiver_id = ?", (ctx.author.id,))
            if cursor.fetchone() is None:
                await ctx.send(f"No marriage proposals for {ctx.author.mention}.")
                return
            cursor.execute("UPDATE MarriageRequests SET accepted = 1 WHERE receiver_id = ?", (ctx.author.id,))
            cursor.execute("DELETE FROM MarriageRequests WHERE accepted = 1 AND receiver_id = ?", (ctx.author.id,))
            self.conn.commit()
            await ctx.send(f"{ctx.author.mention} has accepted the marriage proposal.")
        except Error as e:
            print(e)

    @commands.command()
    async def show_family(self, ctx):
        """Shows the family tree of the author."""
        await ctx.send(f"Showing family tree for {ctx.author.mention}.")

async def setup(bot):
    await bot.add_cog(Family(bot))
