from discord.ext import commands

class AddBotToPlayground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1139581391462473858
        self.role_id = 1139528802482016348

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            role = member.guild.get_role(self.role_id)
            if role:
                await member.add_roles(role)
                channel = self.bot.get_channel(self.channel_id)
                if channel:
                    await channel.send(f"Assigned role to bot: {role.name}")
                else:
                    print("Channel not found. Make sure the channel ID is correct in the code.")
            else:
                print("Role not found. Make sure the role ID is correct in the code.")

    @commands.command(usage="!addbot <client ID>")
    async def addbot(self, ctx, client_id: int):
        """Adds a bot using its client ID."""
        invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=0&scope=bot"
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(f"Invite this bot using the following link: {invite_link}")
        else:
            await ctx.send("Channel not found. Make sure the channel ID is correct in the code.")

async def setup(bot):
    bot.add_cog(AddBotToPlayground(bot))
