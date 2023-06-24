from discord.ext import commands
import sqlite3
import random

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_dict = {}
        self.conn = sqlite3.connect('./data/roles.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS roles
                     (guild_id INTEGER, join_role INTEGER, verify_role INTEGER)''')
        self.conn.commit()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_join_role(self, ctx, role: commands.RoleConverter):
        """Sets the role to give to users when they first join."""
        self.c.execute("INSERT OR REPLACE INTO roles VALUES (?, ?, (SELECT verify_role FROM roles WHERE guild_id=?))", (ctx.guild.id, role.id, ctx.guild.id))
        self.conn.commit()
        await ctx.send(f"Join role has been set to {role.name}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_verify_role(self, ctx, role: commands.RoleConverter):
        """Sets the role to give to users when they are verified."""
        self.c.execute("INSERT OR REPLACE INTO roles VALUES (?, (SELECT join_role FROM roles WHERE guild_id=?), ?)", (ctx.guild.id, ctx.guild.id, role.id))
        self.conn.commit()
        await ctx.send(f"Verify role has been set to {role.name}.")

    @commands.command()
    async def verify(self, ctx):
        """Sends a verification CAPTCHA to the user's DMs and alerts the user to check their DMs."""
        verification_number = random.randint(100, 999)
        self.verification_dict[ctx.author.id] = verification_number
        await ctx.author.send(f"Please respond with this number to verify that you are a human: {verification_number}")
        await ctx.send(f"{ctx.author.mention}, I've sent you a DM with your verification number!", delete_after=20)
        await ctx.message.delete(delay=20)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Assigns the join role to new members."""
        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (member.guild.id,))
        join_role_id = self.c.fetchone()
        if join_role_id is not None:
            join_role = member.guild.get_role(join_role_id[0])
            if join_role is not None:
                await member.add_roles(join_role)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks the user's response to the verification CAPTCHA."""
        if not message.guild and self.verification_dict.get(message.author.id) == int(message.content):
            await message.author.send("Verification successful!")
            guild = self.bot.get_guild(message.author.guild.id)
            self.c.execute("SELECT verify_role FROM roles WHERE guild_id=?", (guild.id,))
            verify_role_id = self.c.fetchone()
            if verify_role_id is not None:
                verify_role = guild.get_role(verify_role_id[0])
                if verify_role is not None:
                    await message.author.add_roles(verify_role)
            self.verification_dict.pop(message.author.id, None)  # remove used captcha
        elif not message.guild and message.author.id in self.verification_dict:
            await message.author.send("Verification failed.")

async def setup(bot):
    await bot.add_cog(Verification(bot))
