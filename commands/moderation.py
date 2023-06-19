from discord.ext import commands
import discord
import sqlite3
import os

DATABASE_PATH = './data/allowed_mods.db'
MOD_ROLE_TABLE = 'mod_roles'

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Initialize database
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()
        self.c.execute(f"CREATE TABLE IF NOT EXISTS {MOD_ROLE_TABLE} (guild_id integer, role_id integer)")

    @commands.command()
    async def info(self, ctx, member: discord.Member):
        """Pulls info from a user."""
        await ctx.send(f'User: {member.name}, ID: {member.id}, Status: {member.status}, Joined at: {member.joined_at}')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addmod(self, ctx, role: discord.Role):
        """Adds a role to allow moderation."""
        self.c.execute(f"INSERT INTO {MOD_ROLE_TABLE} VALUES (?, ?)", (ctx.guild.id, role.id))
        self.conn.commit()
        await ctx.send(f'Role {role.name} has been added as mod role.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removemod(self, ctx, role: discord.Role):
        """Removes a role to allow moderation."""
        self.c.execute(f"DELETE FROM {MOD_ROLE_TABLE} WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
        self.conn.commit()
        await ctx.send(f'Role {role.name} has been removed from mod roles.')

    async def cog_check(self, ctx):
        # Check if the command invoker has mod role or is the owner
        if ctx.guild is not None and ctx.guild.owner_id == ctx.author.id:
            return True

        self.c.execute(f"SELECT role_id FROM {MOD_ROLE_TABLE} WHERE guild_id = ?", (ctx.guild.id,))
        mod_roles = self.c.fetchall()
        mod_roles = [role[0] for role in mod_roles]
        member_roles = [role.id for role in ctx.author.roles]
        return set(mod_roles).intersection(set(member_roles))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
