from discord.ext import commands
import sqlite3
from sqlite3 import Error

class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.create_connection()

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect('./data/family.db') 
            print(sqlite3.version)
        except Error as e:
            print(e)
        return conn

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
            await ctx.send(f"{ctx.author.mention} has sent an adoption request to {member.mention}.")
        except Error as e:
            print(e)

    @commands.command()
    async def accept_adoption(self, ctx):
        """Accepts an adoption request."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM AdoptionRequests WHERE receiver_id = ?", (ctx.author.id,))
            if cursor.fetchone() is None:
                await ctx.send(f"No adoption requests for {ctx.author.mention}.")
                return
            cursor.execute("UPDATE AdoptionRequests SET accepted = 1 WHERE receiver_id = ?", (ctx.author.id,))
            cursor.execute("DELETE FROM AdoptionRequests WHERE accepted = 1 AND receiver_id = ?", (ctx.author.id,))
            self.conn.commit()
            await ctx.send(f"{ctx.author.mention} has accepted the adoption request.")
        except Error as e:
            print(e)

    @commands.command()
    async def reject_adoption(self, ctx):
        """Rejects an adoption request."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM AdoptionRequests WHERE receiver_id = ?", (ctx.author.id,))
            self.conn.commit()
            await ctx.send(f"{ctx.author.mention} has rejected the adoption request.")
        except Error as e:
            print(e)

    @commands.command()
    async def propose(self, ctx, *, member: discord.Member):
        """Sends a marriage proposal to another member."""
        if ctx.author == member:
            await ctx.send(f"{ctx.author.mention}, you cannot send a marriage proposal to yourself.")
            return
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO MarriageRequests(sender_id, receiver_id) VALUES (?, ?)", (ctx.author.id, member.id))
            self.conn.commit()
            await ctx.send(f"{ctx.author.mention} has sent a marriage proposal to {member.mention}.")
        except Error as e:
            print(e)

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
