from discord.ext import commands
import sqlite3
from sqlite3 import Error

class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.create_connection()

    def create_connection(self):
        conn = None;
        try:
            conn = sqlite3.connect('./data/family.db') 
            print(sqlite3.version)
        except Error as e:
            print(e)
        return conn

    @commands.command()
    async def adopt(self, ctx, *, member: discord.Member):
        """Sends an adoption request to another member."""
        await ctx.send(f"{ctx.author.mention} has sent an adoption request to {member.mention}.")

    @commands.command()
    async def accept_adoption(self, ctx):
        """Accepts an adoption request."""
        await ctx.send(f"{ctx.author.mention} has accepted the adoption request.")

    @commands.command()
    async def show_family(self, ctx):
        """Shows the family tree of the author."""
        await ctx.send(f"Showing family tree for {ctx.author.mention}.")

async def setup(bot):
    bot.add_cog(Family(bot))
