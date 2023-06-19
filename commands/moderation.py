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
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a user out of the server."""
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kick')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a user from the server."""
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Unbans a user."""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'User {user} has been unbanned')
                return

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount : int):
        """Clears a specified amount of messages in the channel."""
        await ctx.channel.purge(limit=amount)

    # You would need a role named 'Muted' created and its permissions set to disallow sending messages or adding reactions in every channel.
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes a user."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=False)

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"User {member} has been muted")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a user."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            await ctx.send("No 'Muted' role found. The user could not have been muted.")
            return

        await member.remove_roles(muted_role)
        await ctx.send(f"User {member} has been unmuted")

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

        # Set the user's avatar or a default avatar
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar)

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
