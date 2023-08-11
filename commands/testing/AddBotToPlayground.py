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

    @tasks.loop(minutes=60)  # Adjust the interval as needed
    async def check_bots(self):
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            bot_client_ids = []

            for guild in self.bot.guilds:
                for member in guild.members:
                    if member.bot:
                        bot_client_ids.append(member.id)

            if bot_client_ids:
                client_ids_text = "\n".join(str(client_id) for client_id in bot_client_ids)
                await channel.send(f"List of bot client IDs in servers:\n{client_ids_text}")
                
                for client_id in bot_client_ids:
                    await self.send_bot_invite(channel, client_id)
        else:
            print("Channel not found. Make sure the channel ID is correct in the code.")

    async def send_bot_invite(self, channel, client_id):
        invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=0&scope=bot"
        
        async for message in channel.history():
            if self.bot.user.id == message.author.id and invite_link in message.content:
                return  # Invite link is already in the channel, no need to send it again

        await channel.send(f"Invite this bot using the following link: {invite_link}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            role = member.guild.get_role(self.role_id)
            if role:
                await member.add_roles(role)
                channel = self.bot.get_channel(self.channel_id)
                if channel:
                    await channel.send(f"Assigned role to bot: {role.name}")
                    async for message in channel.history():
                        if self.bot.user.id == message.author.id and "client_id=" in message.content:
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