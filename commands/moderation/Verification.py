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
    async def show_roles(self, ctx):
        """Shows the set join and verify roles for the guild."""
        
        # Query the database for the roles
        self.c.execute("SELECT join_role, verify_role FROM roles WHERE guild_id=?", (ctx.guild.id,))
        roles = self.c.fetchone()
        
        # If we couldn't fetch the roles from the database
        if roles is None:
            await ctx.send("No entry found for this guild in the database.")
            return
    
        join_role, verify_role = roles
    
        # If either role ID is None, inform the user
        if join_role is None or verify_role is None:
            await ctx.send(f"Fetched roles from database:\nJoin Role ID: {join_role}\nVerify Role ID: {verify_role}")
            return
    
        join_role_obj = ctx.guild.get_role(join_role)
        verify_role_obj = ctx.guild.get_role(verify_role)
        
        # If we can't fetch the Role objects from the guild
        if join_role_obj is None or verify_role_obj is None:
            await ctx.send(f"One or both of the roles don't exist anymore in this server.\nJoin Role ID: {join_role}\nVerify Role ID: {verify_role}")
            return
    
        await ctx.send(f"Join Role: {join_role_obj.name}\nVerify Role: {verify_role_obj.name}")
        
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
        
        # Fetch the current join_role from the database
        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (ctx.guild.id,))
        join_role_id = self.c.fetchone()
        if join_role_id is None:  # If no record exists for the guild
            self.c.execute("INSERT INTO roles (guild_id, verify_role) VALUES (?, ?)", (ctx.guild.id, role.id))
        else:
            self.c.execute("UPDATE roles SET verify_role=? WHERE guild_id=?", (role.id, ctx.guild.id))
        
        self.conn.commit()
        await ctx.send(f"Verify role has been set to {role.name}.")
    
    @commands.command()
    async def verify(self, ctx):
        """Sends a verification CAPTCHA to the user's DMs and alerts the user to check their DMs."""
        verification_number = random.randint(100, 999)
        self.verification_dict[ctx.author.id] = (verification_number, ctx.guild.id)
        await ctx.author.send(f"Please respond with this number to verify that you are a human: {verification_number}")
        await ctx.send(f"{ctx.author.mention}, I've sent you a DM with your verification number!", delete_after=20)
        await ctx.message.delete(delay=20)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return  # Skip the process for bots
        
        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (member.guild.id,))
        join_role_id = self.c.fetchone()
        if join_role_id is not None:
            join_role = member.guild.get_role(join_role_id[0])
            if join_role is not None:
                await member.add_roles(join_role)
            
    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks the user's response to the verification CAPTCHA."""
        verification_data = self.verification_dict.get(message.author.id)
    
        if not message.guild and verification_data and int(message.content) == verification_data[0]:
            await message.author.send("Verification successful!")
            
            # Log the guild ID we're fetching
            print(f"Fetching guild with ID: {verification_data[1]}")
            
            # Get the correct guild using the stored guild ID
            guild = self.bot.get_guild(verification_data[1])
            
            if guild:
                member = guild.get_member(message.author.id)
                
                # Add the verify role
                self.c.execute("SELECT verify_role FROM roles WHERE guild_id=?", (guild.id,))
                verify_role_id = self.c.fetchone()
                if verify_role_id:
                    verify_role = guild.get_role(verify_role_id[0])
                    if verify_role:
                        print(f"Adding verify role {verify_role.name} to {member.name}")
                        await member.add_roles(verify_role)
                    else:
                        print(f"Verify role with ID {verify_role_id[0]} not found in guild {guild.name}")
                else:
                    print(f"No verify role ID found for guild {guild.name}")
    
                # Remove the join role
                self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (guild.id,))
                join_role_id = self.c.fetchone()
                if join_role_id:
                    join_role = guild.get_role(join_role_id[0])
                    if join_role:
                        print(f"Removing join role {join_role.name} from {member.name}")
                        await member.remove_roles(join_role)
                    else:
                        print(f"Join role with ID {join_role_id[0]} not found in guild {guild.name}")
                else:
                    print(f"No join role ID found for guild {guild.name}")
    
                self.verification_dict.pop(message.author.id, None)  # remove used captcha
    
        elif not message.guild and message.author.id in self.verification_dict:
            await message.author.send("Verification failed.")
                
async def setup(bot):
    await bot.add_cog(Verification(bot))
