from discord.ext import commands
import discord
import sqlite3
import os
from discord import Embed, Color

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

        # Create a new embed message
        embed = Embed(title=f"User Info: {member.name}", color=Color.blue())

        # Fill in the embed message
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="User Name", value=member.display_name, inline=True)
        embed.add_field(name="Created At", value=member.created_at.strftime("%#d %B %Y, %I:%M %p UTC"), inline=True)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%#d %B %Y, %I:%M %p UTC"), inline=False)
        embed.add_field(name="Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)

        if member.premium_since is not None:
            embed.add_field(name="Boosting Since", value=member.premium_since.strftime("%#d %B %Y, %I:%M %p UTC"), inline=False)

        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

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
