from discord.ext import commands
import random

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_dict = {}

    @commands.command()
    async def verify(self, ctx):
        """Sends a verification CAPTCHA to the user's DMs."""
        verification_number = random.randint(100, 999)
        self.verification_dict[ctx.author.id] = verification_number
        await ctx.author.send(f"Please respond with this number to verify that you are a human: {verification_number}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks the user's response to the verification CAPTCHA."""
        if not message.guild and self.verification_dict.get(message.author.id) == int(message.content):
            await message.author.send("Verification successful!")
            self.verification_dict.pop(message.author.id, None)  # remove used captcha
        elif not message.guild and message.author.id in self.verification_dict:
            await message.author.send("Verification failed.")

async def setup(bot):
    await bot.add_cog(Verification(bot))
