from discord.ext import commands
import discord

class MentalHealthSupportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Specific list of trigger words
        trigger_words = [
            "kms", "suicide", "self harm", "selfharm", "end my life", 
            "kill myself", "harming myself", "no one cares", "give up",
            "killing myself"
        ]

        # Check if any trigger word is in the message and if the author is not the bot
        if any(word in message.content.lower() for word in trigger_words) and message.author != self.bot.user:
            embed = discord.Embed(
                title="It's Okay to Ask for Help",
                description=("It seems like you might be going through a tough time. If you need someone to talk to, there are people who can help. "
                             "Here are some resources and support numbers."),
                color=discord.Color.blue()
            )
            embed.add_field(name="Crisis Support Numbers", value="[Click here for resources](https://github.com/Exohayvan/atsuko/blob/main/documents/Crisis-Support-Numbers.md)", inline=False)
            embed.set_footer(text="Remember, you are not alone.")

            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MentalHealthSupportCog(bot))