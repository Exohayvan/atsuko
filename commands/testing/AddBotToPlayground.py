import discord
from discord.ext import commands, tasks

class AddBotToPlayground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1139728971211214928
        self.role_id = 1139528802482016348

        self.check_bots.start()  # Start the task

    def cog_unload(self):
        self.check_bots.cancel()  # Cancel the task when the cog unloads

    @tasks.loop(minutes=60)
    async def check_bots(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print("DEBUG: Channel not found. Make sure the channel ID is correct in the code.")
            return

        bot_client_ids_in_guild = set()  # Bots in the specific server
        bot_client_ids_in_channel = set()  # Bots mentioned in the channel

        # 1. Gather every single bot in the specific server's client ID
        for member in channel.guild.members:
            if member.bot:
                bot_client_ids_in_guild.add(member.id)

        # 2. Check if the bot's client ID exists in the channel
        async for message in channel.history(limit=None):
            if self.bot.user.id == message.author.id and "client_id=" in message.content:
                client_id_in_msg = message.content.split("client_id=")[1].split("&")[0]
                bot_client_ids_in_channel.add(client_id_in_msg)

        # 3. Check conditions: if it's not in the server AND its client ID isn't in the channel, send the invite
        for client_id in bot_client_ids_in_guild:
            client_id_str = str(client_id)
            if client_id_str not in bot_client_ids_in_channel:
                print(f"DEBUG: Sending invite for bot with client ID: {client_id_str}")
                await self.send_bot_invite(channel, client_id_str)
            else:
                if client_id_str in bot_client_ids_in_channel:
                    print(f"DEBUG: Skipping bot with client ID: {client_id_str} as it's already mentioned in the channel")
                else:
                    print(f"DEBUG: Skipping bot with client ID: {client_id_str} as it's already in the server")
            
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
                        if message.author == self.bot.user and f"client_id={member.id}" in message.content:
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