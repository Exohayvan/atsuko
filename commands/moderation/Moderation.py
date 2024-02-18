import sqlite3
import json
from discord.ext import commands
from discord import Embed, Color, PermissionOverwrite
import discord
from discord.ext.commands import CheckFailure

DATABASE_PATH = './data/allowed_mods.db'
MOD_ROLE_TABLE = 'mod_roles'
LOCK_DB_PATH = './data/channel_locking.db'

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Initialize database for mod roles
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()
        self.c.execute(f"CREATE TABLE IF NOT EXISTS {MOD_ROLE_TABLE} (guild_id integer, role_id integer)")

        # Initialize database for channel locking
        self.lock_conn = sqlite3.connect(LOCK_DB_PATH)
        self.lock_c = self.lock_conn.cursor()
        self.lock_c.execute('''CREATE TABLE IF NOT EXISTS locks
                               (channel_id TEXT PRIMARY KEY, permissions TEXT)''')

    @commands.command(usage="!lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """Locks a channel."""
        # Save the original permissions
        permissions = {str(target): {
            'type': str(type(target)),
            'permissions': overwrite.to_pair()
        } for target, overwrite in ctx.channel.overwrites.items()}
        permissions_json = json.dumps(permissions)
        self.lock_c.execute("INSERT OR REPLACE INTO locks VALUES (?, ?)", (str(ctx.channel.id), permissions_json))
        self.lock_conn.commit()

        # Deny send_messages permission for every role
        for role in ctx.guild.roles:
            await ctx.channel.set_permissions(role, overwrite=PermissionOverwrite(send_messages=False))

        await ctx.send("Channel locked.")
                
    @commands.command(usage="!unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        """Unlocks a channel."""
        self.lock_c.execute("SELECT permissions FROM locks WHERE channel_id = ?", (str(ctx.channel.id),))
        result = self.lock_c.fetchone()
        if result:
            # Restore the original permissions
            permissions = json.loads(result[0])
            for target, overwrite in permissions.items():
                target_type = overwrite['type']
                if "Role" in target_type:
                    target = ctx.guild.get_role(int(target))
                else:
                    target = await self.bot.fetch_user(int(target))

                if target:
                    overwrite = PermissionOverwrite.from_pair(
                        discord.Permissions(overwrite['permissions'][0]),
                        discord.Permissions(overwrite['permissions'][1])
                    )
                    await ctx.channel.set_permissions(target, overwrite=overwrite)
            await ctx.send("Channel unlocked.")
        else:
            await ctx.send("Channel was not previously locked.")

    @commands.command(usage="!kick <@mention>")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a user out of the server."""
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kick')

    @commands.command(usage="!setprefix <prefix you want> (This can be literaly anything you like, just please make it a normal one please.)")
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, prefix=None):
        if prefix is None:
            await ctx.send("Please provide a prefix. *Ex: !setprefix ?*")
            return
        conn = sqlite3.connect('./data/prefix.db')
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO prefixes (guild_id, prefix) VALUES (?, ?)", (ctx.guild.id, prefix))
        conn.commit()
        conn.close()
        await ctx.send(f"The prefix has been set to '{prefix}'")
        
    @commands.command(usage="!ban <@mention>")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a user from the server."""
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned')

    @commands.command(usage="!unban <userID>")
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

    @commands.command(usage="!purge <number of messages>")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount : int):
        """Clears a specified amount of messages in the channel."""
        await ctx.channel.purge(limit=amount)

    # You would need a role named 'Muted' created and its permissions set to disallow sending messages or adding reactions in every channel.
    @commands.command(usage="!mute <@mention>")
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

    @commands.command(usage="!unmute <@mention>")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a user."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            await ctx.send("No 'Muted' role found. The user could not have been muted.")
            return

        await member.remove_roles(muted_role)
        await ctx.send(f"User {member} has been unmuted")

    @commands.command(usage="!user <mention>")
    async def user(self, ctx, member: discord.Member):
        """Shows info about the mentioned user."""

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

    @commands.command(usage="!addmod <@mention>")
    @commands.has_permissions(administrator=True)
    async def addmod(self, ctx, role: discord.Role):
        """Adds a role to allow moderation."""
        self.c.execute(f"INSERT INTO {MOD_ROLE_TABLE} VALUES (?, ?)", (ctx.guild.id, role.id))
        self.conn.commit()
        await ctx.send(f'Role {role.name} has been added as mod role.')

    @commands.command(usage="!removemod <@mention>")
    @commands.has_permissions(administrator=True)
    async def removemod(self, ctx, role: discord.Role):
        """Removes a role to allow moderation."""
        self.c.execute(f"DELETE FROM {MOD_ROLE_TABLE} WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
        self.conn.commit()
        await ctx.send(f'Role {role.name} has been removed from mod roles.')

    async def cog_check(self, ctx):
        try:
            # Check if the command invoker has mod role or is the owner
            if ctx.guild is not None and ctx.guild.owner_id == ctx.author.id:
                return True
    
            self.c.execute(f"SELECT role_id FROM {MOD_ROLE_TABLE} WHERE guild_id = ?", (ctx.guild.id,))
            mod_roles = self.c.fetchall()
            mod_roles = [role[0] for role in mod_roles]
            member_roles = [role.id for role in ctx.author.roles]
            return bool(set(mod_roles).intersection(set(member_roles)))
        except CheckFailure:
            await ctx.sent("Sorry you don't appear to have permissions to do that")
            return False  # This will disallow the command if a CheckFailure occurs
        except Exception as e:
            print(f"Error in cog_check: {e}")  # Logs other errors for debugging
            return False  # Default to not allowing the command if there's an error
                        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            #await ctx.send("You don't have the required permissions to use this command! If you believe you should have permission to use this command, ask server owner to use `!addmod <mod role>` to add permissions to role.")
            print(".")
            
async def setup(bot):
    await bot.add_cog(Moderation(bot))
