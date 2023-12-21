from discord.ext import commands
import discord
import os

class MentalHealthSupportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trigger_words = self.load_trigger_words()

    def load_trigger_words(self):
        trigger_words = []
        directory = '.data/txt/mentaltriggers'
        
        # Loop through each file in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                    # Add each line as a trigger word
                    trigger_words.extend(line.strip() for line in file if line.strip())
        return trigger_words

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if any trigger word is in the message and if the author is not the bot
        if any(word in message.content.lower() for word in self.trigger_words) and message.author != self.bot.user:
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