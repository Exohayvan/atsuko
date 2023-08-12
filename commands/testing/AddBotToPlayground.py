import discord
from discord.ext import commands, tasks

class AddBotToPlayground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1139581391462473858
        self.role_id = 1139528802482016348

        self.check_bots.start()  # Start the task

    def cog_unload(self):
        self.check_bots.cancel()  # Cancel the task when the cog unloads

    @tasks.loop(minutes=60)
    async def check_bots(self):
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            bot_client_ids_in_guild = set()  # Use a set for faster lookup
            bot_client_ids_in_channel = set()
    
            # Gather bot IDs in messages in the channel
            async for message in channel.history(limit=None):  # Fetch all messages
                if self.bot.user.id == message.author.id and "client_id=" in message.content:
                    client_id_in_msg = message.content.split("client_id=")[1].split("&")[0]
                    bot_client_ids_in_channel.add(client_id_in_msg)
    
            # Gather bot IDs from all servers the bot is in
            for guild in self.bot.guilds:
                for member in guild.members:
                    if member.bot:
                        bot_client_ids_in_guild.add(member.id)
    
            # Check each bot
            for client_id in bot_client_ids_in_guild:
                # If the bot is not already in the channel messages
                if str(client_id) not in bot_client_ids_in_channel:
                    print("DEBUG: Sent invite to channel")
                    await self.send_bot_invite(channel, client_id)
        else:
            print("Channel not found. Make sure the channel ID is correct in the code.")
                                                    
    async def send_bot_invite(self, channel, client_id):
        invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=0&scope=bot"
        
        async for message in channel.history():
            if self.bot.user.id == message.author.id and invite_link in message.content:
                print("DEBUG: Skipping bot invite link due to already existing in channel")
                return  # Invite link is already in the channel, no need to send it again
        
        await channel.send(f"[{client_id}]({invite_link})")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            role = member.guild.get_role(self.role_id)
            if role:
                await member.add_roles(role)
                channel = self.bot.get_channel(self.channel_id)
                if channel:
                    async for message in channel.history():
                        if message.author == self.bot.user and f"client_id={self.bot.user.id}" in message.content:
                            await message.delete()
                else:
                    print("Channel not found. Make sure the channel ID is correct in the code.")
            else:
                print("Role not found. Make sure the role ID is correct in the code.")
            
    @commands.command(usage="!addbot <client ID>")
    async def addbot(self, ctx, client_id: int):
        """Adds a bot using its client ID."""
        invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=0&scope=bot"
        
        # Check if the bot is already in the server
        bot_member = ctx.guild.get_member(client_id)
        if bot_member:
            await ctx.send("The bot is already in the server.")
            return
        
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await self.send_bot_invite(channel, client_id)
        else:
            await ctx.send("Channel not found. Make sure the channel ID is correct in the code.")

async def setup(bot):
    await bot.add_cog(AddBotToPlayground(bot))